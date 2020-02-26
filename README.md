ESP32-Setup
===========

Basis setup:

    $ source ~/esp-env/bin/activate
    $ export PORT=/dev/cu.SLAB_USBtoUART

Copying files:

    $ pyboard.py --device $PORT -f cp main.py :

REPL:

    $ screen $PORT 115200

---

Ideally you'd encrypt your WLAN password with an AES key printed on the device.

This would mean only that particular device, with the key pre-installed, could decrypt your password. It would also mean that only the person who's got the devise and can read the printed key can take constrol of it, i.e. register it with their WLAN.

However an AES key is at minimum 128 bits, i.e. 32 hex digits, which is more than most people would want to type in - and you'd probably want to include two checksum digits so that it's possible to point out if the key looks good or not.

One possibility would be to use a [password-based key derivation function](https://en.wikipedia.org/wiki/Key_derivation_function) (PBKDF) to generate a key from a more reasonable length password (see step 5. and the text below in this Crypto StackExchange [answer](https://crypto.stackexchange.com/a/53554/8854)). Currently [Argon2](https://en.wikipedia.org/wiki/Argon2) seems to be the first-choice PBKDF, however according to this [answer](https://forum.micropython.org/viewtopic.php?p=36116#p36116) on the MicroPython forums all such algorithms consume noticeable amounts of ROM "unlikely to ever appear by default in micropython firmware".

---

Currently `main.py` pulls in just MicroWebSrv2 and MicroDNSSrv.

slimDNS on its own is pulled in with `main-mdns.py` - to install it instead of `main.py`:

    $ pyboard.py --device $PORT -f cp main-mdns.py :main.py

To query the names advertised by `main-mdns.py`:

    $ dig @224.0.0.251 -p 5353 portal.local
    $ dig @224.0.0.251 -p 5353 dns.local

To see all the queries that slimDNS sees, i.e. not just the ones relating to names that it's advertising, uncomment the `print` in `compare_packed_names`.

My Mac automatically tried to query for all these names:

```
_airplay
_airport
_apple-mobdev
_apple-pairable
_companion-link
_googlecast
_ipp
_ipps
_ippusb
_pdl-datastream
_printer
_ptp
_raop
_rdlink
_scanner
_sleep-proxy
_uscan
_uscans
```

---

Using slimDNS to lookup `dns.local` and then MicroDNSSrv to respond to any arbitrary name:

    $ dig +short @dns.local foobar

If you've overriden your nameserver to something like [8.8.8.8](https://en.wikipedia.org/wiki/Google_Public_DNS) then this is quite slow (I suspect it first tries to resolve `dns.local` via DNS and only then falls back to trying mDNS). In such a situation it's noticeably faster to explicitly resolve `dns.local` via mDNS:

    $ nameserver=$(dig +short @224.0.0.251 -p 5353 dns.local)
    $ dig +short @$nameserver foobar

If you haven't overriden your nameserver, i.e. just accept the one configured when you connect to an AP, then the `@nameserver` can be omitted altogether:

    $ dig +short foobar

---

About 100 lines of `slimDNS.py` involves code to detect name clashes, e.g. if you use the name `alpha` it checks first to see if something else is already advertising this name.

I removed this code and in doing so I also removed `resolve_mdns_address`, i.e. the ability to resolve mDNS addresses - now the code can only advertise addresses.

---

Look at what affect using [mpy-cross](https://github.com/micropython/micropython/tree/master/mpy-cross) has on available memory.

You can check available memory like so:

    >>> import micropython
    >>> micropython.mem_info()
    ...
    >>> import gc
    >>> gc.collect()
    >>> micropython.mem_info()
    ...

Maybe it makes no difference _once things are compiled_ but simply ensures that the compiler won't run out of memory doing its job?

---

Sources:

* https://github.com/jczic/MicroWebSrv2
* https://github.com/nickovs/slimDNS/blob/638c461/slimDNS.py
* https://github.com/jczic/MicroDNSSrv/blob/ebe69ff/microDNSSrv.py

---

Note `LICENSE.md` is from MicroDNSSrv rather than being a license actively chosen by me.

---

You can dump the visible access points like so:

    >>> json.dumps([(t[0], binascii.hexlify(t[1]), t[2]) for t in sta.scan()])

When using the REPL, it escapes single quotes, i.e. "Foo's AP" is displayed as "Foo\'s AP", which is invalid JSON. This is just a REPL artifact. To get the un-munged JSOM:

    >>> import network
    >>> import json
    >>> import binascii
    >>> sta = network.WLAN(network.STA_IF)
    >>> sta.active(True)
    >>> with open('data.json', 'w') as f:
    >>>     json.dump([(t[0], binascii.hexlify(t[1]), t[2]) for t in sta.scan()], f)

    $ pyboard.py --device $PORT -f cp :data.json data.json

The results (prettified) are something like this:

```json
[
  [
    "UPC Wi-Free",
    "3a431d3e4ec7",
    1
  ],
  [
    "Salt_2GHz_8A9F85",
    "44fe3b8a9f87",
    11
  ],
  [
    "JB_40",
    "488d36d5c83a",
    11
  ],
  [
    "Sonja’s iPhone",
    "664de20a139f",
    6
  ],
  ...
```