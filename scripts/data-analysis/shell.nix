{ pkgs ? import <nixpkgs> { } }:

pkgs.mkShell {
  name = "cif-env";

  buildInputs = with pkgs; [
    python312
    (python312.withPackages (ps: with ps; [ numpy pandas matplotlib ]))
  ];

  shellHook = ''
    python main.py
  '';
}
