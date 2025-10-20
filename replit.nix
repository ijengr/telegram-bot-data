{ pkgs }: {
  deps = [
    pkgs.python3
    pkgs.python3Packages.pip
    pkgs.python3Packages.virtualenv
    # Untuk handle SSL certificates
    pkgs.cacert
    pkgs.openssl
  ];
}
