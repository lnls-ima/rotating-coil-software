

!define APPNAME "Campo_34401A"									; nome do aplicativo (nome do executável)
!define SETUPNAME "setup_Campo34401A.exe"							; nome do instalador
!define FILEPATH "D:\ARQ\Work_at_LNLS\ICE\Projetos\Agilent_34401A\build\exe.win-amd64-3.2\"		; diretório do executável




!include "MUI2.nsh"

Name "${APPNAME}"

OutFile "${SETUPNAME}"

InstallDir "$PROGRAMFILES\${APPNAME}"

;--------------------------------
;Configuracoes da interface

!define MUI_ABORTWARNING

;paginas de instalacao
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

;paginas de desinstalacao
!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

;Idioma
!insertmacro MUI_LANGUAGE "PortugueseBR"

;--------------------------------
; The stuff to install
Section "${APPNAME} (required)"

  SectionIn RO
  
  SetOutPath $INSTDIR
  File /r "${FILEPATH}"
  
  WriteUninstaller "$INSTDIR\Uninstall.exe"

  SetShellVarContext all
  CreateDirectory "$SMPROGRAMS\${APPNAME}"
  CreateShortCut "$SMPROGRAMS\${APPNAME}\Uninstall.lnk" "$INSTDIR\uninstall.exe"
  CreateShortCut "$SMPROGRAMS\${APPNAME}\${APPNAME}.lnk" "$INSTDIR\${APPNAME}.exe"
  
SectionEnd

;--------------------------------
; Uninstaller
Section "Uninstall"

  SetShellVarContext all
  RMDir /r "$SMPROGRAMS\${APPNAME}"
  RMDir /r "$INSTDIR"

SectionEnd
