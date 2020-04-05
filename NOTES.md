ESP32-Setup
===========

If you've created your venv before you open the project in PyCharm then it will automatically pickup the Python version from the venv. Otherwise, go toSettings / Project:my-project-name / Project Interpreter - click cog and select _Add_, it should automatically select _Existing environment_ and the interpreter in the venv - you just have to press OK.

---

To test the timeout logic that expires sockets try:

    $ telnet $ADDR 80

Just leave it there or paste in e.g. just the first line of a request:

    GET / HTTP/1.1

Within 2 seconds (the time configured via `SlimConfig.timeout_sec`) the server will drop the connection.

---

It's not currently possible to report why connecting to an access point fails, e.g. an invalid password.

For more details, see my MicroPython [forum post](https://forum.micropython.org/viewtopic.php?t=7942) about how `WLAN.status()` currently works.

---

Ideally you'd encrypt your WLAN password with an AES key printed on the device.

This would mean only that particular device, with the key pre-installed, could decrypt your password. It would also mean that only the person who's got the devise and can read the printed key can take constrol of it, i.e. register it with their WLAN.

However an AES key is at minimum 128 bits, i.e. 32 hex digits, which is more than most people would want to type in - and you'd probably want to include two checksum digits so that it's possible to point out if the key looks good or not.

One possibility would be to use a [password-based key derivation function](https://en.wikipedia.org/wiki/Key_derivation_function) (PBKDF) to generate a key from a more reasonable length password (see step 5. and the text below in this Crypto StackExchange [answer](https://crypto.stackexchange.com/a/53554/8854)). Currently [Argon2](https://en.wikipedia.org/wiki/Argon2) seems to be the first-choice PBKDF, however according to this [answer](https://forum.micropython.org/viewtopic.php?p=36116#p36116) on the MicroPython forums all such algorithms consume noticeable amounts of ROM "unlikely to ever appear by default in micropython firmware".

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
    "Sonja's iPhone",
    "664de20a139f",
    6
  ],
  ...
```

---

If you're posting data using `curl` you won't see the data even with `-v` as it doesn't show the body content that's sent:

    $ curl -v --data 'bssid=alpha&password=beta' 192.168.0.178/authenticate

If you want to see the headers _and_ body content, you have to replace `-v` with `--trace-ascii -` like so:

    $ curl --trace-ascii - --data 'bssid=alpha&password=beta' 192.168.0.178/authenticate

---

Black and Flake8
----------------

The code is formatted with [Black](https://black.readthedocs.io/en/stable/) and checked with [Flake8](https://flake8.pycqa.org/en/latest/).

    $ pip install black
    $ pip install flake8

To reformat, provide a list of files and/or directories to `black`:

    $ black ...

To check, provide a list of files and/or directories to `flake8`:

    $ flake8 ... | fgrep -v -e E501 -e E203 -e E722

Here `fgrep` is used to ignore E501 (line too long) and E203 (whitespace before ':') as these are rules that Black and Flake8 disagree on. I also ignore E203 (do not use bare 'except') as I'm not prepared to enforce this rule in the code.