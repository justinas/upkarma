{ pkgs ? import <nixpkgs> { }
, poetry2nix ? pkgs.poetry2nix
, karmaDesign ? ../karma_design
}:
let
  src = ./.;
  code = pkgs.stdenv.mkDerivation {
    name = "upkarma";
    inherit src;

    buildPhase = "";
    installPhase = ''
      mkdir -p $out/share/src/upkarma
      cp -r $src/. $out/share/src/upkarma
    '';
  };
in
code // { deploy = pkgs.callPackage ./deploy.nix { inherit code karmaDesign; }; }
