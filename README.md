

# IPFS Desktop
https://github.com/ipfs-shipyard/ipfs-desktop

afterwards `ln -s /Applications/IPFS\ Desktop.app/Contents/Resources/app.asar.unpacked/node_modules/go-ipfs/go-ipfs/ipfs ~/bin/ipfs`

## disable localhost subdomain
```
ipfs config --json Gateway.PublicGateways '{
    "localhost": {
      "UseSubdomains": false,
      "Paths": ["/ipfs", "/ipns"]
    }
  }'
```

# keep alive
```
./refresh_contents.py keep_alive cid of directory
```
example:
```
./refresh_contents.py keep_alive QmU4LAxfpsY5A7pzYPetwLoAj8txmLKUUU2EeRaLQx2KsH --gateway=dweb.link -s
```


# generate m3u8
```
./refresh_contents.py m3u8 cid of directory
```
example:
```
./refresh_contents.py m3u8 QmU4LAxfpsY5A7pzYPetwLoAj8txmLKUUU2EeRaLQx2KsH --gateway=dweb.link
```