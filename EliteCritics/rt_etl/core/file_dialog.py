"""
core.file_dialog
=================

Acesso ao seletor de arquivos moderno do Windows (o mesmo utilizado pelo
Explorer, com painel de navegação lateral e locais rapidos) atraves da
interface COM `IFileOpenDialog`.

A implementacao utiliza exclusivamente `ctypes` e chamadas nativas do
Windows (ole32.dll / shell32.dll). Nenhuma biblioteca de terceiros
(pywin32, comtypes) e nenhum framework de interface grafica generico
(Tkinter, PySide6, PyQt, Flask etc.) e utilizado, em conformidade com os
requisitos do projeto.

Este modulo expoe apenas duas funcoes publicas:

    pick_file(title, file_types)   -> caminho de arquivo selecionado
    pick_folder(title)             -> caminho de pasta selecionada

Ambas retornam `None` caso o usuario cancele a operacao.
"""

from __future__ import annotations

import sys
import ctypes
from ctypes import wintypes, POINTER, byref, c_void_p, c_wchar_p

_IS_WINDOWS = sys.platform == "win32"


class FileDialogUnavailableError(RuntimeError):
    """Levantada quando o seletor nativo do Windows nao pode ser utilizado."""


if _IS_WINDOWS:
    ole32 = ctypes.OleDLL("ole32")
    shell32 = ctypes.OleDLL("shell32")

    # ------------------------------------------------------------------
    # Constantes COM
    # ------------------------------------------------------------------
    CLSCTX_INPROC_SERVER = 0x1
    COINIT_APARTMENTTHREADED = 0x2

    CLSID_FileOpenDialog = "{DC1C5A9C-E88A-4dde-A5A1-60F82A20AEF7}"
    IID_IFileOpenDialog = "{d57c7288-d4ad-4768-be02-9d969532d960}"
    IID_IShellItem = "{43826d1e-e718-42ee-bc55-a1e261c37bfe}"

    # Flags de FILEOPENDIALOGOPTIONS relevantes
    FOS_PICKFOLDERS = 0x00000020
    FOS_FORCEFILESYSTEM = 0x00000040
    FOS_FILEMUSTEXIST = 0x00001000
    FOS_PATHMUSTEXIST = 0x00000800

    SIGDN_FILESYSPATH = 0x80058000

    HRESULT = ctypes.c_long

    class GUID(ctypes.Structure):
        _fields_ = [
            ("Data1", ctypes.c_ulong),
            ("Data2", ctypes.c_ushort),
            ("Data3", ctypes.c_ushort),
            ("Data4", ctypes.c_ubyte * 8),
        ]

        def __init__(self, guid_str: str):
            super().__init__()
            ole32.CLSIDFromString(c_wchar_p(guid_str), byref(self))

    class COMDLG_FILTERSPEC(ctypes.Structure):
        _fields_ = [
            ("pszName", c_wchar_p),
            ("pszSpec", c_wchar_p),
        ]

    # ------------------------------------------------------------------
    # Definicao minima das vtables COM necessarias (IUnknown, IShellItem,
    # IModalWindow, IFileDialog, IFileOpenDialog). A ordem dos ponteiros
    # de funcao segue exatamente a ordem declarada nos cabecalhos publicos
    # do Windows SDK (shobjidl_core.h).
    # ------------------------------------------------------------------

    class IUnknownVtbl(ctypes.Structure):
        _fields_ = [
            ("QueryInterface", ctypes.WINFUNCTYPE(HRESULT, c_void_p, POINTER(GUID), POINTER(c_void_p))),
            ("AddRef", ctypes.WINFUNCTYPE(ctypes.c_ulong, c_void_p)),
            ("Release", ctypes.WINFUNCTYPE(ctypes.c_ulong, c_void_p)),
        ]

    class IShellItemVtbl(ctypes.Structure):
        _fields_ = [
            ("QueryInterface", ctypes.WINFUNCTYPE(HRESULT, c_void_p, POINTER(GUID), POINTER(c_void_p))),
            ("AddRef", ctypes.WINFUNCTYPE(ctypes.c_ulong, c_void_p)),
            ("Release", ctypes.WINFUNCTYPE(ctypes.c_ulong, c_void_p)),
            ("BindToHandler", ctypes.WINFUNCTYPE(HRESULT, c_void_p, c_void_p, POINTER(GUID), POINTER(GUID), POINTER(c_void_p))),
            ("GetParent", ctypes.WINFUNCTYPE(HRESULT, c_void_p, POINTER(c_void_p))),
            ("GetDisplayName", ctypes.WINFUNCTYPE(HRESULT, c_void_p, ctypes.c_ulong, POINTER(c_wchar_p))),
            ("GetAttributes", ctypes.WINFUNCTYPE(HRESULT, c_void_p, ctypes.c_ulong, POINTER(ctypes.c_ulong))),
            ("Compare", ctypes.WINFUNCTYPE(HRESULT, c_void_p, c_void_p, ctypes.c_uint, POINTER(ctypes.c_int))),
        ]

    class IShellItem(ctypes.Structure):
        pass

    IShellItem._fields_ = [("lpVtbl", POINTER(IShellItemVtbl))]

    class IFileDialogVtbl(ctypes.Structure):
        _fields_ = [
            ("QueryInterface", ctypes.WINFUNCTYPE(HRESULT, c_void_p, POINTER(GUID), POINTER(c_void_p))),
            ("AddRef", ctypes.WINFUNCTYPE(ctypes.c_ulong, c_void_p)),
            ("Release", ctypes.WINFUNCTYPE(ctypes.c_ulong, c_void_p)),
            ("Show", ctypes.WINFUNCTYPE(HRESULT, c_void_p, wintypes.HWND)),
            ("SetFileTypes", ctypes.WINFUNCTYPE(HRESULT, c_void_p, ctypes.c_uint, POINTER(COMDLG_FILTERSPEC))),
            ("SetFileTypeIndex", ctypes.WINFUNCTYPE(HRESULT, c_void_p, ctypes.c_uint)),
            ("GetFileTypeIndex", ctypes.WINFUNCTYPE(HRESULT, c_void_p, POINTER(ctypes.c_uint))),
            ("Advise", ctypes.WINFUNCTYPE(HRESULT, c_void_p, c_void_p, POINTER(ctypes.c_ulong))),
            ("Unadvise", ctypes.WINFUNCTYPE(HRESULT, c_void_p, ctypes.c_ulong)),
            ("SetOptions", ctypes.WINFUNCTYPE(HRESULT, c_void_p, ctypes.c_ulong)),
            ("GetOptions", ctypes.WINFUNCTYPE(HRESULT, c_void_p, POINTER(ctypes.c_ulong))),
            ("SetDefaultFolder", ctypes.WINFUNCTYPE(HRESULT, c_void_p, c_void_p)),
            ("SetFolder", ctypes.WINFUNCTYPE(HRESULT, c_void_p, c_void_p)),
            ("GetFolder", ctypes.WINFUNCTYPE(HRESULT, c_void_p, POINTER(c_void_p))),
            ("GetCurrentSelection", ctypes.WINFUNCTYPE(HRESULT, c_void_p, POINTER(c_void_p))),
            ("SetFileName", ctypes.WINFUNCTYPE(HRESULT, c_void_p, c_wchar_p)),
            ("GetFileName", ctypes.WINFUNCTYPE(HRESULT, c_void_p, POINTER(c_wchar_p))),
            ("SetTitle", ctypes.WINFUNCTYPE(HRESULT, c_void_p, c_wchar_p)),
            ("SetOkButtonLabel", ctypes.WINFUNCTYPE(HRESULT, c_void_p, c_wchar_p)),
            ("SetFileNameLabel", ctypes.WINFUNCTYPE(HRESULT, c_void_p, c_wchar_p)),
            ("GetResult", ctypes.WINFUNCTYPE(HRESULT, c_void_p, POINTER(c_void_p))),
            ("AddPlace", ctypes.WINFUNCTYPE(HRESULT, c_void_p, c_void_p, ctypes.c_int)),
            ("SetDefaultExtension", ctypes.WINFUNCTYPE(HRESULT, c_void_p, c_wchar_p)),
            ("Close", ctypes.WINFUNCTYPE(HRESULT, c_void_p, HRESULT)),
            ("SetClientGuid", ctypes.WINFUNCTYPE(HRESULT, c_void_p, POINTER(GUID))),
            ("ClearClientData", ctypes.WINFUNCTYPE(HRESULT, c_void_p)),
            ("SetFilter", ctypes.WINFUNCTYPE(HRESULT, c_void_p, c_void_p)),
        ]

    class IFileOpenDialogVtbl(ctypes.Structure):
        _fields_ = IFileDialogVtbl._fields_ + [
            ("GetResults", ctypes.WINFUNCTYPE(HRESULT, c_void_p, POINTER(c_void_p))),
            ("GetSelectedItems", ctypes.WINFUNCTYPE(HRESULT, c_void_p, POINTER(c_void_p))),
        ]

    class IFileOpenDialog(ctypes.Structure):
        pass

    IFileOpenDialog._fields_ = [("lpVtbl", POINTER(IFileOpenDialogVtbl))]

    def _check(hresult: int, operation: str) -> None:
        if hresult < 0:
            raise FileDialogUnavailableError(
                f"Falha na operacao COM '{operation}' (HRESULT=0x{hresult & 0xFFFFFFFF:08X})."
            )

    def _get_path_from_result(dialog_ptr) -> str | None:
        """Extrai o caminho de sistema de arquivos do IShellItem de resultado."""
        item_ptr = c_void_p()
        hr = dialog_ptr.contents.lpVtbl.contents.GetResult(dialog_ptr, byref(item_ptr))
        if hr < 0 or not item_ptr:
            return None

        item = ctypes.cast(item_ptr, POINTER(IShellItem))
        name_ptr = c_wchar_p()
        hr = item.contents.lpVtbl.contents.GetDisplayName(item, SIGDN_FILESYSPATH, byref(name_ptr))
        item.contents.lpVtbl.contents.Release(item)

        if hr < 0 or not name_ptr.value:
            return None

        path = str(name_ptr.value)
        ole32.CoTaskMemFree(name_ptr)
        return path

    def _run_dialog(title: str, options_extra: int, file_types: list[tuple[str, str]] | None) -> str | None:
        ole32.CoInitializeEx(None, COINIT_APARTMENTTHREADED)
        try:
            clsid = GUID(CLSID_FileOpenDialog)
            iid = GUID(IID_IFileOpenDialog)
            dialog_ptr = c_void_p()

            hr = ole32.CoCreateInstance(
                byref(clsid), None, CLSCTX_INPROC_SERVER, byref(iid), byref(dialog_ptr)
            )
            _check(hr, "CoCreateInstance(FileOpenDialog)")

            dialog = ctypes.cast(dialog_ptr, POINTER(IFileOpenDialog))
            vtbl = dialog.contents.lpVtbl.contents

            base_options = ctypes.c_ulong()
            vtbl.GetOptions(dialog, byref(base_options))
            new_options = base_options.value | FOS_FORCEFILESYSTEM | FOS_PATHMUSTEXIST | options_extra
            vtbl.SetOptions(dialog, new_options)

            if title:
                vtbl.SetTitle(dialog, c_wchar_p(title))

            if file_types:
                specs = (COMDLG_FILTERSPEC * len(file_types))()
                for idx, (name, pattern) in enumerate(file_types):
                    specs[idx].pszName = c_wchar_p(name)
                    specs[idx].pszSpec = c_wchar_p(pattern)
                vtbl.SetFileTypes(dialog, len(file_types), specs)

            hr = vtbl.Show(dialog, None)
            if hr < 0:
                # Cancelamento pelo usuario (HRESULT_FROM_WIN32(ERROR_CANCELLED))
                # ou falha na exibicao: em ambos os casos, nao ha selecao.
                return None

            result = _get_path_from_result(dialog)
            vtbl.Release(dialog)
            return result
        finally:
            ole32.CoUninitialize()

    def pick_file(title: str = "Selecionar arquivo", file_types: list[tuple[str, str]] | None = None) -> str | None:
        """Abre o seletor de arquivo nativo do Windows e retorna o caminho escolhido."""
        return _run_dialog(title, FOS_FILEMUSTEXIST, file_types)

    def pick_folder(title: str = "Selecionar pasta") -> str | None:
        """Abre o seletor de pasta nativo do Windows e retorna o caminho escolhido."""
        return _run_dialog(title, FOS_PICKFOLDERS, None)

else:
    def pick_file(title: str = "Selecionar arquivo", file_types=None) -> str | None:
        raise FileDialogUnavailableError(
            "O seletor de arquivos nativo depende da API COM do Windows e nao esta "
            "disponivel neste sistema operacional."
        )

    def pick_folder(title: str = "Selecionar pasta") -> str | None:
        raise FileDialogUnavailableError(
            "O seletor de pastas nativo depende da API COM do Windows e nao esta "
            "disponivel neste sistema operacional."
        )
