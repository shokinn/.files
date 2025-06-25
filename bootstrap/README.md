# Bootstrap

## Get "data" Value from defaults

1. Export the defaults
   ```shell
   defaults export com.jordanbaird.Ice -
   ```
2. Copy the base64 encoded data to a new file (`base64`), remove all whitespace, save it
3. Run this command to convert the data to hex
   ```shell
   cat ./base64| base64 -d | xxd -p | tr -d '\n' > ./hex
   ```
4. Copy the whole hex data and use it like the following with defaults:
   ```shell
   defaults write com.jordanbaird.Ice MenuBarAppearanceConfigurationV2 -data <hex data>
   ```

## Export plist file

```shell
defaults export com.jordanbaird.Ice ~/.files/config/plist/Ice.plist
```
