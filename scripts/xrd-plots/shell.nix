{ pkgs ? import <nixpkgs> { } }:

pkgs.mkShell {
  name = "plot";

  buildInputs = with pkgs; [
    python312
    (python312.withPackages (ps: with ps; [ numpy matplotlib plotly ]))
  ];

  shellHook = ''
    Done!
  '';
}
