!define APP_NAME      "PTMusic"
!define APP_VERSION   "26.6.8"
!define APP_PUBLISHER "Phoni Technology"
!define APP_URL       "https://www.youtube.com/@Phoni1RBX"
!define APP_EXE       "PTMusic.exe"
!define INST_DIR      "$PROGRAMFILES64\Phoni Technology\PTMusic"
!define REG_KEY       "Software\Microsoft\Windows\CurrentVersion\Uninstall\PTMusic"

Unicode True
SetCompressor /SOLID lzma

;---- Installer appearance ----
!include "MUI2.nsh"
!define MUI_ABORTWARNING
!define MUI_ICON    "PTMusic.ico"
!define MUI_UNICON  "PTMusic.ico"

Name         "${APP_NAME} ${APP_VERSION}"
OutFile      "PTMusic_Setup.exe"
InstallDir   "${INST_DIR}"
InstallDirRegKey HKLM "${REG_KEY}" "InstallLocation"
RequestExecutionLevel admin

;---- Pages ----
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!define MUI_FINISHPAGE_RUN      "$INSTDIR\${APP_EXE}"
!define MUI_FINISHPAGE_RUN_TEXT "Launch PTMusic"
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "English"

;---- Install section ----
Section "PTMusic" SecMain
    SetOutPath "$INSTDIR"
    File "dist\PTMusic.exe"
    File "PTMusic.png"
    File "PTMusic.ico"
    IfFileExists "$EXEDIR\Montserrat-SemiBold.ttf" 0 +2
        File "Montserrat-SemiBold.ttf"

    ; Start Menu shortcut
    CreateDirectory "$SMPROGRAMS\Phoni Technology"
    CreateShortcut  "$SMPROGRAMS\Phoni Technology\PTMusic.lnk" \
                    "$INSTDIR\${APP_EXE}" "" "$INSTDIR\PTMusic.ico"

    ; Desktop shortcut
    CreateShortcut  "$DESKTOP\PTMusic.lnk" \
                    "$INSTDIR\${APP_EXE}" "" "$INSTDIR\PTMusic.ico"

    ; Add/Remove Programs entry
    WriteRegStr   HKLM "${REG_KEY}" "DisplayName"     "${APP_NAME}"
    WriteRegStr   HKLM "${REG_KEY}" "DisplayVersion"  "${APP_VERSION}"
    WriteRegStr   HKLM "${REG_KEY}" "Publisher"       "${APP_PUBLISHER}"
    WriteRegStr   HKLM "${REG_KEY}" "URLInfoAbout"    "${APP_URL}"
    WriteRegStr   HKLM "${REG_KEY}" "InstallLocation" "$INSTDIR"
    WriteRegStr   HKLM "${REG_KEY}" "DisplayIcon"     "$INSTDIR\PTMusic.ico"
    WriteRegStr   HKLM "${REG_KEY}" "UninstallString" "$INSTDIR\Uninstall.exe"
    WriteRegDWORD HKLM "${REG_KEY}" "NoModify"        1
    WriteRegDWORD HKLM "${REG_KEY}" "NoRepair"        1

    WriteUninstaller "$INSTDIR\Uninstall.exe"
SectionEnd

;---- Uninstall section ----
Section "Uninstall"
    Delete "$INSTDIR\${APP_EXE}"
    Delete "$INSTDIR\PTMusic.png"
    Delete "$INSTDIR\PTMusic.ico"
    Delete "$INSTDIR\Uninstall.exe"
    RMDir  "$INSTDIR"
    RMDir  "$PROGRAMFILES64\Phoni Technology"

    Delete "$SMPROGRAMS\Phoni Technology\PTMusic.lnk"
    RMDir  "$SMPROGRAMS\Phoni Technology"
    Delete "$DESKTOP\PTMusic.lnk"

    DeleteRegKey HKLM "${REG_KEY}"
SectionEnd
