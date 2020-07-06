{ pkgs, code, karmaDesign }:
let
  design = pkgs.stdenv.mkDerivation {
    name = "upkarma-design";
    src = karmaDesign;
    nativeBuildInputs = with pkgs; [ lessc yuicompressor ];
    buildPhase = "";
    installPhase = ''
      mkdir -p $out/share/src/karma_design/static
      bash -c 'OUT=$out/share/src/karma_design/static source $src/design.sh full'
    '';
  };
  env = pkgs.poetry2nix.mkPoetryEnv {
    projectDir = "${code}/share/src/upkarma";
  };
in
pkgs.symlinkJoin {
  name = "upkarma-deploy";
  paths = [ code design env ];
}
