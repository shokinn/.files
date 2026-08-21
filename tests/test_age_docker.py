from __future__ import annotations

import json
import os
import signal
import subprocess
import tempfile
import time
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / "dotfiles/local/bin/age-docker"


class AgeDockerCliTests(unittest.TestCase):
    def run_cli(
        self,
        *arguments: str,
        cwd: Path,
        env: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [str(SCRIPT), *arguments],
            cwd=cwd,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )

    def make_identity(self, root: Path, name: str = "identity") -> tuple[Path, str]:
        identity = root / name
        generated = subprocess.run(
            ["age-keygen", "-o", str(identity)],
            text=True,
            capture_output=True,
            check=True,
        )
        public_key = next(
            line.removeprefix("Public key: ")
            for line in generated.stderr.splitlines()
            if line.startswith("Public key: ")
        )
        return identity, public_key

    def make_ssh_public_key(self, root: Path, name: str) -> str:
        private_key = root / name
        subprocess.run(
            ["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-f", str(private_key)],
            check=True,
        )
        fields = private_key.with_suffix(".pub").read_text().split()
        return f"{fields[0]} {fields[1]}"

    def write_policy(
        self,
        root: Path,
        personal: str,
        server: str,
        secret: str = "secrets/prod.env.age",
    ) -> None:
        (root / ".age-docker.toml").write_text(
            f'''version = 1

[keys]
phg = "{personal}"
server = "{server}"

[groups]
users = ["phg"]
production = ["server"]

[secrets]
"{secret}" = ["users", "production"]
'''
        )

    def test_init_creates_a_versioned_empty_config_without_overwriting_it(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)

            created = self.run_cli("init", cwd=root)

            self.assertEqual(created.returncode, 0, created.stderr)
            config = root / ".age-docker.toml"
            self.assertEqual(
                config.read_text(),
                "version = 1\n\n[keys]\n\n[groups]\n\n[secrets]\n",
            )

            refused = self.run_cli("init", cwd=root)
            self.assertNotEqual(refused.returncode, 0)
            self.assertIn("already exists", refused.stderr)

    def test_init_honors_the_config_environment_override(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            destination = root / "policy.toml"

            result = self.run_cli(
                "init",
                cwd=root,
                env={**os.environ, "AGE_DOCKER_CONFIG": str(destination)},
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(destination.is_file())
            self.assertFalse((root / ".age-docker.toml").exists())

    def test_identity_environment_default_and_explicit_override(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            identity, personal = self.make_identity(root, "personal")
            _, server = self.make_identity(root, "server")
            self.write_policy(root, personal, server)
            plaintext = root / "secret.txt"
            plaintext.write_text("secret\n")
            encrypted = root / "secrets/prod.env.age"

            from_environment = self.run_cli(
                "encrypt",
                str(plaintext),
                str(encrypted),
                cwd=root,
                env={**os.environ, "AGE_DOCKER_IDENTITY": str(identity)},
            )
            explicit_override = self.run_cli(
                "--identity",
                str(identity),
                "decrypt",
                str(encrypted),
                str(root / "decrypted.txt"),
                cwd=root,
                env={**os.environ, "AGE_DOCKER_IDENTITY": str(root / "missing")},
            )

            self.assertEqual(from_environment.returncode, 0, from_environment.stderr)
            self.assertEqual(explicit_override.returncode, 0, explicit_override.stderr)

    def test_identity_is_required_only_for_identity_dependent_commands(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _, personal = self.make_identity(root, "personal")
            _, server = self.make_identity(root, "server")
            self.write_policy(root, personal, server)
            env = {key: value for key, value in os.environ.items() if key != "AGE_DOCKER_IDENTITY"}

            checked = self.run_cli("check", cwd=root, env=env)
            plaintext = root / "secret.txt"
            plaintext.write_text("secret\n")
            encrypted = self.run_cli(
                "encrypt",
                str(plaintext),
                str(root / "secrets/prod.env.age"),
                cwd=root,
                env=env,
            )

            self.assertEqual(checked.returncode, 0, checked.stderr)
            self.assertNotEqual(encrypted.returncode, 0)
            self.assertIn("AGE_DOCKER_IDENTITY", encrypted.stderr)

    def test_completion_generators_emit_valid_self_contained_shell_code(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for shell in ("bash", "zsh"):
                with self.subTest(shell=shell):
                    generated = self.run_cli("completion", shell, cwd=root)

                    self.assertEqual(generated.returncode, 0, generated.stderr)
                    self.assertIn("_age_docker", generated.stdout)
                    self.assertIn("completion", generated.stdout)
                    syntax = subprocess.run(
                        [shell, "-n"],
                        input=generated.stdout,
                        text=True,
                        capture_output=True,
                        check=False,
                    )
                    self.assertEqual(syntax.returncode, 0, syntax.stderr)

    def test_age_docker_contains_no_runtime_dotdrop_templates(self) -> None:
        templates = [
            line
            for line in SCRIPT.read_text().splitlines()
            if "{{@@" in line or "{%@@" in line
        ]

        self.assertEqual(templates, ["# {{@@ header() @@}}"])

    def test_edit_changes_plaintext_but_a_noop_editor_preserves_ciphertext(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            personal_identity, personal = self.make_identity(root, "personal")
            _, server = self.make_identity(root, "server")
            self.write_policy(root, personal, server)
            plaintext = root / "initial.env"
            plaintext.write_text("TOKEN=before\n")
            encrypted = root / "secrets/prod.env.age"
            created = self.run_cli(
                "--identity",
                str(personal_identity),
                "encrypt",
                str(plaintext),
                str(encrypted),
                cwd=root,
            )
            self.assertEqual(created.returncode, 0, created.stderr)

            editor = root / "editor"
            editor.write_text('#!/bin/sh\nprintf "TOKEN=after\\n" > "$1"\n')
            editor.chmod(0o700)
            editor_env = {
                **os.environ,
                "VISUAL": str(editor),
                "EDITOR": "/usr/bin/false",
            }
            changed = self.run_cli(
                "--identity",
                str(personal_identity),
                "edit",
                str(encrypted),
                cwd=root,
                env=editor_env,
            )
            changed_ciphertext = encrypted.read_bytes()

            self.assertEqual(changed.returncode, 0, changed.stderr)
            decrypted = subprocess.run(
                [
                    "age",
                    "--decrypt",
                    "--identity",
                    str(personal_identity),
                    str(encrypted),
                ],
                capture_output=True,
                check=True,
            ).stdout
            self.assertEqual(decrypted, b"TOKEN=after\n")

            noop_env = {**os.environ, "VISUAL": "/usr/bin/true"}
            noop = self.run_cli(
                "--identity",
                str(personal_identity),
                "edit",
                str(encrypted),
                cwd=root,
                env=noop_env,
            )

            self.assertEqual(noop.returncode, 0, noop.stderr)
            self.assertIn("unchanged", noop.stdout)
            self.assertEqual(encrypted.read_bytes(), changed_ciphertext)

    def test_check_and_list_resolve_nested_recipient_groups(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _, personal = self.make_identity(root, "personal")
            _, server = self.make_identity(root, "server")
            (root / ".age-docker.toml").write_text(
                f'''version = 1

[keys]
phg = "{personal}"
sbx0docker01 = "{server}"

[groups]
users = ["phg"]
production = ["sbx0docker01"]
prod_access = ["users", "production"]

[secrets]
"secrets/prod.env.age" = ["prod_access"]
'''
            )

            checked = self.run_cli("check", cwd=root)
            listed = self.run_cli("list", cwd=root)

            self.assertEqual(checked.returncode, 0, checked.stderr)
            self.assertIn("1 secret", checked.stdout)
            self.assertEqual(listed.returncode, 0, listed.stderr)
            self.assertEqual(
                listed.stdout,
                "secrets/prod.env.age: phg, sbx0docker01\n",
            )

    def test_encrypt_and_decrypt_use_configured_recipients_and_safe_output(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            personal_identity, personal = self.make_identity(root, "personal")
            server_identity, server = self.make_identity(root, "server")
            self.write_policy(root, personal, server)
            plaintext = root / "prod.env"
            plaintext.write_text("TOKEN=correct-horse\n")
            encrypted = root / "secrets/prod.env.age"

            encrypted_result = self.run_cli(
                "--identity",
                str(personal_identity),
                "encrypt",
                str(plaintext),
                str(encrypted),
                cwd=root,
            )

            self.assertEqual(encrypted_result.returncode, 0, encrypted_result.stderr)
            self.assertTrue(
                encrypted.read_text().startswith("-----BEGIN AGE ENCRYPTED FILE-----")
            )
            server_plaintext = subprocess.run(
                [
                    "age",
                    "--decrypt",
                    "--identity",
                    str(server_identity),
                    str(encrypted),
                ],
                capture_output=True,
                check=True,
            ).stdout
            self.assertEqual(server_plaintext, b"TOKEN=correct-horse\n")

            output = root / "decrypted.env"
            decrypted_result = self.run_cli(
                "--identity",
                str(personal_identity),
                "decrypt",
                str(encrypted),
                str(output),
                cwd=root,
            )
            refused = self.run_cli(
                "--identity",
                str(personal_identity),
                "decrypt",
                str(encrypted),
                str(output),
                cwd=root,
            )

            self.assertEqual(decrypted_result.returncode, 0, decrypted_result.stderr)
            self.assertEqual(output.read_text(), "TOKEN=correct-horse\n")
            self.assertEqual(output.stat().st_mode & 0o777, 0o600)
            self.assertNotEqual(refused.returncode, 0)
            self.assertIn("already exists", refused.stderr)

    def test_rekey_all_changes_nothing_on_failure_then_uses_updated_recipients(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            personal_identity, personal = self.make_identity(root, "personal")
            _, old_server = self.make_identity(root, "old-server")
            new_server_identity, new_server = self.make_identity(root, "new-server")
            config = root / ".age-docker.toml"

            def write_config(server: str) -> None:
                config.write_text(
                    f'''version = 1

[keys]
phg = "{personal}"
server = "{server}"

[groups]
deployment = ["phg", "server"]

[secrets]
"secrets/one.age" = ["deployment"]
"secrets/two.age" = ["deployment"]
'''
                )

            write_config(old_server)
            for name in ("one", "two"):
                plaintext = root / f"{name}.txt"
                plaintext.write_text(f"secret-{name}\n")
                result = self.run_cli(
                    "--identity",
                    str(personal_identity),
                    "encrypt",
                    str(plaintext),
                    str(root / f"secrets/{name}.age"),
                    cwd=root,
                )
                self.assertEqual(result.returncode, 0, result.stderr)

            first = root / "secrets/one.age"
            second = root / "secrets/two.age"
            original_first = first.read_bytes()
            original_second = second.read_bytes()
            write_config(new_server)
            second.write_text("not age ciphertext\n")

            failed = self.run_cli(
                "--identity",
                str(personal_identity),
                "rekey",
                "--all",
                cwd=root,
            )

            self.assertNotEqual(failed.returncode, 0)
            self.assertEqual(first.read_bytes(), original_first)

            second.write_bytes(original_second)
            succeeded = self.run_cli(
                "--identity",
                str(personal_identity),
                "rekey",
                "--all",
                cwd=root,
            )

            self.assertEqual(succeeded.returncode, 0, succeeded.stderr)
            for name in ("one", "two"):
                decrypted = subprocess.run(
                    [
                        "age",
                        "--decrypt",
                        "--identity",
                        str(new_server_identity),
                        str(root / f"secrets/{name}.age"),
                    ],
                    capture_output=True,
                    check=True,
                ).stdout
                self.assertEqual(decrypted, f"secret-{name}\n".encode())

    def test_key_scan_preserves_config_format_and_remove_refuses_referenced_keys(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _, personal = self.make_identity(root, "personal")
            scanned_key = self.make_ssh_public_key(root, "host-key")
            config = root / ".age-docker.toml"
            config.write_text(
                f'''version = 1

[keys]
# This comment and surrounding policy must survive key edits.
phg = "{personal}"

[groups]
users = ["phg"]

[secrets]
"secrets/prod.age" = ["users"]
'''
            )
            fake_bin = root / "bin"
            fake_bin.mkdir()
            fake_keyscan = fake_bin / "ssh-keyscan"
            fake_keyscan.write_text(
                f'#!/bin/sh\n[ "$4" = "ed25519" ] || exit 9\nprintf "example.test {scanned_key}\\n"\n'
            )
            fake_keyscan.chmod(0o700)
            env = {**os.environ, "PATH": f"{fake_bin}:{os.environ['PATH']}"}

            scanned = self.run_cli(
                "key",
                "scan",
                "server",
                "example.test",
                "--yes",
                cwd=root,
                env=env,
            )

            self.assertEqual(scanned.returncode, 0, scanned.stderr)
            self.assertIn("SHA256:", scanned.stdout)
            self.assertIn(
                "# This comment and surrounding policy must survive key edits.",
                config.read_text(),
            )
            self.assertIn(f'server = "{scanned_key}"', config.read_text())

            replacement_key = self.make_ssh_public_key(root, "replacement-host-key")
            fake_keyscan.write_text(
                f'#!/bin/sh\n[ "$4" = "ed25519" ] || exit 9\nprintf "example.test {replacement_key}\\n"\n'
            )
            replacement = self.run_cli(
                "key",
                "scan",
                "server",
                "example.test",
                "--replace",
                cwd=root,
                env=env,
            )

            self.assertNotEqual(replacement.returncode, 0)
            self.assertIn("Old:", replacement.stdout)
            self.assertIn("New:", replacement.stdout)
            self.assertIn("--yes", replacement.stderr)

            removed = self.run_cli("key", "remove", "server", cwd=root)
            refused = self.run_cli("key", "remove", "phg", cwd=root)

            self.assertEqual(removed.returncode, 0, removed.stderr)
            self.assertNotIn("server =", config.read_text())
            self.assertNotEqual(refused.returncode, 0)
            self.assertIn("still referenced", refused.stderr)

    def test_mutating_commands_refuse_concurrent_use_of_the_same_policy(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            personal_identity, personal = self.make_identity(root, "personal")
            _, server = self.make_identity(root, "server")
            self.write_policy(root, personal, server)
            plaintext = root / "initial.env"
            plaintext.write_text("TOKEN=value\n")
            encrypted = root / "secrets/prod.env.age"
            created = self.run_cli(
                "--identity",
                str(personal_identity),
                "encrypt",
                str(plaintext),
                str(encrypted),
                cwd=root,
            )
            self.assertEqual(created.returncode, 0, created.stderr)

            ready = root / "editor-ready"
            editor = root / "slow-editor"
            editor.write_text(f'#!/bin/sh\ntouch "{ready}"\nsleep 10\n')
            editor.chmod(0o700)
            env = {**os.environ, "VISUAL": str(editor)}
            first = subprocess.Popen(
                [
                    str(SCRIPT),
                    "--identity",
                    str(personal_identity),
                    "edit",
                    str(encrypted),
                ],
                cwd=root,
                env=env,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=True,
            )
            try:
                deadline = time.monotonic() + 5
                while not ready.exists() and time.monotonic() < deadline:
                    time.sleep(0.05)
                self.assertTrue(ready.exists(), "first editor did not start")

                second = self.run_cli(
                    "--identity",
                    str(personal_identity),
                    "edit",
                    str(encrypted),
                    cwd=root,
                    env={**os.environ, "VISUAL": "/usr/bin/true"},
                )

                self.assertNotEqual(second.returncode, 0)
                self.assertIn("Another age-docker command is active", second.stderr)
            finally:
                os.killpg(first.pid, signal.SIGTERM)
                first.communicate(timeout=5)

    def test_encrypt_preserves_existing_ciphertext_when_personal_access_is_omitted(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            personal_identity, personal = self.make_identity(root, "personal")
            _, server = self.make_identity(root, "server")
            self.write_policy(root, personal, server)
            plaintext = root / "secret.txt"
            plaintext.write_text("before\n")
            encrypted = root / "secrets/prod.env.age"
            created = self.run_cli(
                "--identity",
                str(personal_identity),
                "encrypt",
                str(plaintext),
                str(encrypted),
                cwd=root,
            )
            self.assertEqual(created.returncode, 0, created.stderr)
            original = encrypted.read_bytes()
            (root / ".age-docker.toml").write_text(
                f'''version = 1

[keys]
phg = "{personal}"
server = "{server}"

[groups]
production = ["server"]

[secrets]
"secrets/prod.env.age" = ["production"]
'''
            )
            plaintext.write_text("after\n")

            refused = self.run_cli(
                "--identity",
                str(personal_identity),
                "encrypt",
                str(plaintext),
                str(encrypted),
                cwd=root,
            )

            self.assertNotEqual(refused.returncode, 0)
            self.assertEqual(encrypted.read_bytes(), original)

    def test_check_rejects_cycles_unknown_names_escaping_paths_and_symlinks(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _, personal = self.make_identity(root, "personal")
            cases = {
                "cycle": (
                    f'''version = 1
[keys]
phg = "{personal}"
[groups]
one = ["two"]
two = ["one"]
[secrets]
"secret.age" = ["phg"]
''',
                    "cycle",
                ),
                "unknown": (
                    f'''version = 1
[keys]
phg = "{personal}"
[groups]
users = ["missing"]
[secrets]
"secret.age" = ["users"]
''',
                    "Unknown",
                ),
                "escape": (
                    f'''version = 1
[keys]
phg = "{personal}"
[groups]
users = ["phg"]
[secrets]
"../secret.age" = ["users"]
''',
                    "escapes",
                ),
            }
            for name, (config, message) in cases.items():
                with self.subTest(name=name):
                    (root / ".age-docker.toml").write_text(config)
                    result = self.run_cli("check", cwd=root)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn(message, result.stderr)

            target = root / "actual.age"
            target.touch()
            symlink = root / "secret.age"
            symlink.symlink_to(target)
            (root / ".age-docker.toml").write_text(
                f'''version = 1
[keys]
phg = "{personal}"
[groups]
users = ["phg"]
[secrets]
"secret.age" = ["users"]
'''
            )
            result = self.run_cli("check", cwd=root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("symlink", result.stderr)

    def test_rekey_all_skips_missing_but_explicit_rekey_rejects_it(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            personal_identity, personal = self.make_identity(root, "personal")
            _, server = self.make_identity(root, "server")
            self.write_policy(root, personal, server, secret="secrets/missing.age")

            all_result = self.run_cli(
                "--identity",
                str(personal_identity),
                "rekey",
                "--all",
                cwd=root,
            )
            explicit_result = self.run_cli(
                "--identity",
                str(personal_identity),
                "rekey",
                "secrets/missing.age",
                cwd=root,
            )

            self.assertEqual(all_result.returncode, 0, all_result.stderr)
            self.assertIn("skipping missing", all_result.stderr)
            self.assertNotEqual(explicit_result.returncode, 0)
            self.assertIn("does not exist", explicit_result.stderr)

    def test_key_replacement_requires_explicit_authorization(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _, first = self.make_identity(root, "first")
            _, second = self.make_identity(root, "second")
            initialized = self.run_cli("init", cwd=root)
            self.assertEqual(initialized.returncode, 0, initialized.stderr)
            added = self.run_cli("key", "add", "operator", first, cwd=root)
            refused = self.run_cli("key", "add", "operator", second, cwd=root)
            replaced = self.run_cli(
                "key",
                "add",
                "operator",
                second,
                "--replace",
                "--yes",
                cwd=root,
            )

            self.assertEqual(added.returncode, 0, added.stderr)
            self.assertNotEqual(refused.returncode, 0)
            self.assertIn("--replace", refused.stderr)
            self.assertEqual(replaced.returncode, 0, replaced.stderr)
            self.assertIn(
                f'operator = "{second}"', (root / ".age-docker.toml").read_text()
            )

    def test_edit_removes_plaintext_temporary_files_after_sigterm(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            temp_root = root / "tmp"
            temp_root.mkdir()
            personal_identity, personal = self.make_identity(root, "personal")
            _, server = self.make_identity(root, "server")
            self.write_policy(root, personal, server)
            plaintext = root / "initial.env"
            plaintext.write_text("TOKEN=value\n")
            encrypted = root / "secrets/prod.env.age"
            created = self.run_cli(
                "--identity",
                str(personal_identity),
                "encrypt",
                str(plaintext),
                str(encrypted),
                cwd=root,
            )
            self.assertEqual(created.returncode, 0, created.stderr)

            ready = root / "signal-editor-ready"
            editor = root / "signal-editor"
            editor.write_text(f'#!/bin/sh\ntouch "{ready}"\nsleep 10\n')
            editor.chmod(0o700)
            process = subprocess.Popen(
                [
                    str(SCRIPT),
                    "--identity",
                    str(personal_identity),
                    "edit",
                    str(encrypted),
                ],
                cwd=root,
                env={**os.environ, "VISUAL": str(editor), "TMPDIR": str(temp_root)},
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
            try:
                deadline = time.monotonic() + 5
                while not ready.exists() and time.monotonic() < deadline:
                    time.sleep(0.05)
                self.assertTrue(ready.exists(), "editor did not start")
                process.terminate()
                process.wait(timeout=5)
                self.assertEqual(list(temp_root.glob("age-docker-edit-*")), [])
            finally:
                try:
                    os.killpg(process.pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass

    def test_duplicate_key_aliases_produce_one_recipient_stanza(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            identity, recipient = self.make_identity(root, "personal")
            (root / ".age-docker.toml").write_text(
                f'''version = 1
[keys]
primary = "{recipient}"
duplicate = "{recipient}"
[groups]
users = ["primary", "duplicate"]
[secrets]
"secret.age" = ["users"]
'''
            )
            plaintext = root / "secret.txt"
            plaintext.write_text("secret\n")
            encrypted = root / "secret.age"

            result = self.run_cli(
                "--identity",
                str(identity),
                "encrypt",
                str(plaintext),
                str(encrypted),
                cwd=root,
            )
            inspection = subprocess.run(
                ["age-inspect", "--json", str(encrypted)],
                text=True,
                capture_output=True,
                check=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(inspection.stdout)["stanza_types"], ["X25519"])


if __name__ == "__main__":
    unittest.main()
