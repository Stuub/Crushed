# CVE-2024-4040 SSTI & LFI PoC - Exploitation | CrushFTP 

This is a proof of concept for a Server Side Template Injection (SSTI) & Local File Inclusion (LFI) vulnerability in CrushFTP. 


## Features

Taking leverage of Critical Severity Vulnerabilities in CrushFTP servers through Server Side Template Injection (SSTI) & Authentication Bypassing. Elevating this exploit to a Local File Inclusion (LFI)! This PoC exploit serves a purpose in automating the detection of the vulnerability within sFTP servers hosting CrushFTP, as well as the exploitation!

## Step Through the Code:
- Generation of anonymous session tokens
- Utilising these tokens to perform SSTI and create our own entry-points!
- Calling our SSTI endpoints and escaping out of their context to request any local resource on a target machine!

After doing a little bit of Google dorking, i found there is currently over 7000 publicly accessible CrushFTP portals live today! 😬 This CVE was only disclosed 6 days ago, need i say anymore...

## Usage

`
python3 crushed.py -t https://target.com
`

For Specifying your own LFI path, use `-l` or `--lfi` argument:

`
python3 crushed.py -t https://target.com -l /etc/passwd
`

## Example

![image](https://github.com/Stuub/CVE-2024-4040-SSTI-LFI/assets/60468836/267cfbce-838a-4992-8d44-4a39352aca19)


## Documentation

This vulnerability is a VFS sandbox escape in the CrushFTP managed file transfer service that allows remote attackers with low privileges to read files from the filesystem outside of VFS Sandbox

Server-Side Template Injection (SSTI) in CrushFTP allows an attacker to execute arbitrary code on the server by abusing the "zip" function in the WebInterface.

Affecting CrushFTP versions below 10.7.1 and 11.1.0 (as well as legacy 9.x versions)

## Shodan Dork:

http.favicon.hash:-1022206565

## References

https://attackerkb.com/topics/20oYjlmfXa/cve-2024-4040/rapid7-analysis

## Disclaimer

This tool is purely for ethical and educational purposes only. Use responsibly.
