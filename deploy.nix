{ pkgs, code, karmaDesign }:
let
  design = pkgs.stdenv.mkDerivation {
    name = "upkarma-design";
    src = karmaDesign;
    buildPhase = "";
    installPhase = ''
      mkdir -p $out/share/src/karma_design
      cp -r $src/. $out/share/src/karma_design
    '';
  };
in
pkgs.stdenv.mkDerivation
{
  name = "upkarma-deploy";
  src = pkgs.symlinkJoin {
    name = "upkarma-code-and-design";
    paths = [ code design ];
  };
  buildInputs = [ code design ];
  nativeBuildInputs = with pkgs; [ lessc yuicompressor ];
  buildPhase = ''
    mkdir -p temp/share/src/
    cp -Lr $src/share/src/. temp/share/src # nasty copy :(
    chmod -R 770 temp/share/src/karma_design # nasty chmod :(
    (cd temp/share/src/upkarma && ./design.sh full)
  '';
  installPhase = ''
    ls
    cp -r temp/. $out/
  '';
}
