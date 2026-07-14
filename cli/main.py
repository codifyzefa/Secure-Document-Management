from __future__ import annotations

from typing import Any

from controllers.auth_controller import AuthController
from controllers.audit_controller import AuditController
from controllers.document_controller import DocumentController
from controllers.face_controller import FaceController
from logger.logging_config import get_logger

logger = get_logger(__name__)

# ANSI color codes for improved CLI UX
class _C:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RESET = "\033[0m"


def _ok(msg: str) -> str:
    return f"{_C.GREEN}{msg}{_C.RESET}"


def _err(msg: str) -> str:
    return f"{_C.RED}{msg}{_C.RESET}"


def _info(msg: str) -> str:
    return f"{_C.CYAN}{msg}{_C.RESET}"


def _bold(msg: str) -> str:
    return f"{_C.BOLD}{msg}{_C.RESET}"


WELCOME_ART = rf"""
{_C.CYAN}{_C.BOLD}   +==================================================+
   |       Secure Document Management System  v1.0.0       |
   |                Information Security                    |
   +==================================================+{_C.RESET}
"""

DOC_TABLE_HEADER: str = (
    f"  {_C.DIM}{'DOCUMENT ID':<14} {'FILENAME':<36} {'SIZE':>10}  {'STATUS':<8}{_C.RESET}"
)
DOC_TABLE_SEPARATOR: str = f"  {_C.DIM}{'-' * 72}{_C.RESET}"


def display_welcome() -> None:
    print(WELCOME_ART)


def _is_admin(controller: AuthController) -> bool:
    user = controller.get_current_user()
    return user is not None and user.get("role") == "admin"


def _navigation_prompt() -> str:
    print()
    print(f"  {_bold('[1]')} Perform Again")
    print(f"  {_bold('[2]')} Back")
    print(f"  {_bold('[0]')} Return to Main Menu")
    print()
    return input("  Enter your choice: ").strip()


def _print_document_table(docs: list[dict[str, Any]]) -> None:
    print(DOC_TABLE_HEADER)
    print(DOC_TABLE_SEPARATOR)
    for doc in docs:
        doc_id: str = doc.get("document_id", "")
        filename: str = doc.get("original_filename", "")
        size: str = doc.get("file_size_display", "")
        status: str = doc.get("status", "")
        print(
            f"  {doc_id:<14} {filename:<36} {size:>10}  {status:<8}"
        )


def _print_document_detail(doc: dict[str, Any]) -> None:
    print(f"  {_bold('Document ID')}      : {doc['document_id']}")
    print(f"  {_bold('Filename')}         : {doc['original_filename']}")
    print(f"  {_bold('Type')}             : {doc['mime_type']}")
    print(f"  {_bold('Size')}             : {doc['file_size_display']} ({doc['file_size']:,} bytes)")
    print(f"  {_bold('SHA-256')}          : {doc['sha256_hash']}")
    print(f"  {_bold('Status')}           : {doc['status']}")
    print(f"  {_bold('Shared with')}      : {doc['shared_with_count']} user(s)")
    print(f"  {_bold('Created')}          : {doc['created_at']}")
    print(f"  {_bold('Updated')}          : {doc['updated_at']}")


def _prompt_document_id() -> str | None:
    doc_id: str = input(f"  {_info('Document ID (e.g. DOC-0001)')}: ").strip().upper()
    if not doc_id:
        print(f"  {_err('Operation cancelled')} — Document ID is required.")
        return None
    return doc_id


# ======================================================================
# Main loop
# ======================================================================


def run_cli() -> None:
    logger.info("CLI started — interactive mode.")
    controller = AuthController()
    doc_controller = DocumentController()
    audit_controller = AuditController()
    face_controller = FaceController()

    while True:
        print()
        _print_menu(controller)
        print()

        choice: str = input("  Enter your choice: ").strip()

        if choice in ("0", "exit", "quit"):
            if controller.is_authenticated():
                controller.logout()
            print(f"  {_ok('Goodbye.')}")
            logger.info("CLI session ended by user.")
            break
        elif choice == "1":
            _handle_registration(controller, face_controller)
        elif choice == "2":
            _handle_login(controller)
        elif choice == "3" and controller.is_authenticated():
            _handle_logout(controller)
        elif choice == "3" and not controller.is_authenticated():
            _handle_face_login(face_controller)
        elif choice == "4" and controller.is_authenticated():
            _handle_upload(doc_controller)
        elif choice == "5" and controller.is_authenticated():
            _handle_list_documents(doc_controller)
        elif choice == "6" and controller.is_authenticated():
            _handle_document_detail(doc_controller)
        elif choice == "7" and controller.is_authenticated():
            _handle_search_documents(doc_controller)
        elif choice == "8" and controller.is_authenticated():
            _handle_download(doc_controller)
        elif choice == "9" and controller.is_authenticated():
            _handle_share(doc_controller)
        elif choice == "10" and controller.is_authenticated():
            _handle_shared_documents(doc_controller)
        elif choice == "11" and controller.is_authenticated() and _is_admin(controller):
            _handle_audit_logs(audit_controller)
        elif choice == "12" and controller.is_authenticated() and _is_admin(controller):
            _handle_audit_search(audit_controller)
        elif choice == "13" and controller.is_authenticated():
            _handle_face_settings(face_controller, controller)
        else:
            print(f"  {_err('Invalid choice.')} Please try again.")


def _print_menu(controller: AuthController) -> None:
    sep: str = f"  {_C.DIM}+{'-' * 37}+{_C.RESET}"
    title_sep: str = f"  {_C.CYAN}+{'-' * 37}+{_C.RESET}"
    print(sep)
    if controller.is_authenticated():
        user = controller.get_current_user()
        is_admin: bool = user is not None and user.get("role") == "admin"
        status_line = (
            f"  |  {_C.GREEN}Logged in as {user['username']:<18}{_C.RESET}|"
            if user
            else f"  |  Logged in                              |"
        )
        print(status_line)
        print(title_sep)
        print(f"  |  {_bold('[3]')} Logout                           |")
        print(f"  |  {_bold('[4]')} Upload Document                  |")
        print(f"  |  {_bold('[5]')} My Documents                     |")
        print(f"  |  {_bold('[6]')} Document Details                 |")
        print(f"  |  {_bold('[7]')} Search Documents                 |")
        print(f"  |  {_bold('[8]')} Download Document                |")
        print(f"  |  {_bold('[9]')} Share Document                    |")
        print(f"  |  {_bold('[10]')} Shared With Me                   |")
        if is_admin:
            print(title_sep)
            print(f"  |  {_bold('[11]')} View Audit Logs                 |")
            print(f"  |  {_bold('[12]')} Search Audit Logs               |")
        print(title_sep)
        print(f"  |  {_bold('[13]')} Face Settings                    |")
    else:
        print(f"  |  {_C.CYAN}Main Menu{_C.RESET}                         |")
        print(title_sep)
        print(f"  |  {_bold('[1]')} Register                         |")
        print(f"  |  {_bold('[2]')} Login (Password)                  |")
        print(f"  |  {_bold('[3]')} Login (Face Recognition)          |")
    print(f"  |  {_bold('[0]')} Exit                              |")
    print(sep)


# ======================================================================
# Registration & Login
# ======================================================================


def _handle_registration(
    controller: AuthController,
    face_controller: FaceController,
) -> None:
    print()
    print(f"  {_bold('--- User Registration ---')}")
    print()

    if controller.is_authenticated():
        print(f"  {_err('You are already logged in.')}")
        return

    username: str = input("  Username        : ").strip()
    if not username:
        print(f"  {_err('Registration cancelled')} — username is required.")
        return

    password: str = input("  Password        : ")

    print()
    print(f"  {_info('Available roles: admin, editor, viewer')}")
    role: str = input("  Role            : ").strip().lower()
    if not role:
        print(f"  {_err('Registration cancelled')} — role is required.")
        return

    print()
    print(f"  {_info('Processing registration ...')}")
    result: dict[str, Any] = controller.register(
        username=username, password=password, role=role
    )

    print()
    if result.get("success"):
        print(f"  {_ok(result['message'])}")
        print(f"    {_bold('Username')}  : {result['username']}")
        print(f"    {_bold('Role')}      : {result['role']}")

        print()
        print(f"  {_bold('--- Optional Face Recognition ---')}")
        if not face_controller.is_available():
            print(f"  {_err('Face recognition libraries not available.')} Skipping enrollment.")
            print(f"  {_info('Install opencv-python and face_recognition to enable this feature.')}")
        else:
            choice: str = input(
                f"  {_info('Enable Face Recognition Authentication? (y/n): ')}"
            ).strip().lower()
            if choice == "y":
                _handle_face_enrollment(
                    face_controller,
                    result["user_id"],
                    result["username"],
                )
            else:
                print(
                    f"  {_info('Face recognition not enabled.')} "
                    f"{_info('You can enable it later via [13] Face Settings.')}"
                )
    else:
        print(f"  {_err(result['error'])}")


def _handle_login(controller: AuthController) -> None:
    print()
    print(f"  {_bold('--- User Login ---')}")
    print()

    username: str = input("  Username  : ").strip()
    if not username:
        print(f"  {_err('Login cancelled')} — username is required.")
        return

    password: str = input("  Password  : ")

    print()
    print(f"  {_info('Authenticating ...')}")
    result: dict[str, Any] = controller.login(
        username=username, password=password
    )

    print()
    if result.get("success"):
        print(f"  {_ok(result['message'])}")
    else:
        print(f"  {_err(result['error'])}")


def _handle_face_login(face_controller: FaceController) -> None:
    print()
    print(f"  {_bold('--- Face Recognition Login ---')}")
    print()

    if not face_controller.is_available():
        print(f"  {_err('Face recognition libraries are not installed.')}")
        print(f"  {_info('Use [2] Login (Password) instead.')}")
        return

    print(f"  {_info('Looking at camera...')}")
    result: dict[str, Any] = face_controller.login_face()

    print()
    if result.get("success"):
        print(f"  {_ok(result['message'])}")
    else:
        print(f"  {_err(result['error'])}")


def _handle_logout(controller: AuthController) -> None:
    result: dict[str, Any] = controller.logout()
    print()
    if result.get("success"):
        print(f"  {_ok(result['message'])}")
    else:
        print(f"  {_err(result['error'])}")


# ======================================================================
# Document Upload
# ======================================================================


def _handle_upload(doc_controller: DocumentController) -> None:
    print()
    print(f"  {_bold('--- Upload Document ---')}")
    print()

    file_path: str = input("  File path  : ").strip().strip("\"'")
    if not file_path:
        print(f"  {_err('Upload cancelled')} — file path is required.")
        return

    print()
    print(f"  {_info('Uploading and encrypting ...')}")
    result: dict[str, Any] = doc_controller.upload(file_path)

    print()
    if result.get("success"):
        print(f"  {_ok(result['message'])}")
        print(f"    {_bold('Document ID')}  : {result['document_id']}")
        print(f"    {_bold('File name')}    : {result['original_filename']}")
        print(f"    {_bold('Size')}         : {result['file_size']:,} bytes")
        print(f"    {_bold('MIME type')}    : {result['mime_type']}")
        print(f"    {_bold('SHA-256')}      : {result['sha256_hash']}")
    else:
        print(f"  {_err(result['error'])}")


# ======================================================================
# Document Listing (My Documents)
# ======================================================================


def _handle_list_documents(doc_controller: DocumentController) -> None:
    while True:
        print()
        print(f"  {_bold('--- My Documents ---')}")
        print()

        page: int = 1
        while True:
            result = doc_controller.list_my_documents(page=page)

            if not result.get("success"):
                print(f"  {_err(result['error'])}")
                break

            documents = result.get("documents", [])
            pagination = result.get("pagination", {})

            if not documents:
                if page == 1:
                    print(f"  {_info('No documents found.')}")
                else:
                    print(f"  {_info('No more documents.')}")
                break

            total = pagination.get("total", 0)
            cur_pg: int = pagination.get("page", 1)
            total_pgs: int = pagination.get("total_pages", 1)
            print(
                f"  {_bold(f'Page {cur_pg}/{total_pgs}')}"
                f"  ({total} document{'s' if total != 1 else ''})"
            )
            print()
            _print_document_table(documents)
            print()

            if pagination.get("has_next"):
                choice: str = input(
                    f"  {_info('[N]ext page, [Q]uit this view: ')}"
                ).strip().lower()
                if choice == "n":
                    page += 1
                    continue
            break

        nav: str = _navigation_prompt()
        if nav == "1":
            continue
        if nav == "2":
            return
        break


def _handle_document_detail(doc_controller: DocumentController) -> None:
    while True:
        print()
        print(f"  {_bold('--- Document Details ---')}")
        print()
        print(f"  {_info('Enter a Document ID to view its full details.')}")
        print()

        doc_id: str | None = _prompt_document_id()
        if doc_id is None:
            return

        print()
        print(f"  {_info('Fetching details ...')}")
        result = doc_controller.get_document_detail(doc_id)

        print()
        if result.get("success"):
            _print_document_detail(result["document"])
        else:
            print(f"  {_err(result['error'])}")

        nav: str = _navigation_prompt()
        if nav == "1":
            continue
        if nav == "2":
            return
        break


# ======================================================================
# Document Search
# ======================================================================


def _handle_search_documents(doc_controller: DocumentController) -> None:
    while True:
        print()
        print(f"  {_bold('--- Search Documents ---')}")
        print()
        print(f"  {_bold('[1]')} Search by Document ID")
        print(f"  {_bold('[2]')} Search by File Name")
        print(f"  {_bold('[3]')} Show All Documents")
        print(f"  {_bold('[0]')} Back")
        print()

        choice: str = input("  Enter your choice: ").strip()

        if choice == "0":
            return

        if choice == "1":
            _search_by_document_id(doc_controller)
        elif choice == "2":
            _search_by_filename(doc_controller)
        elif choice == "3":
            _show_all_documents(doc_controller)
        else:
            print(f"  {_err('Invalid choice.')}")
            continue


def _search_by_document_id(doc_controller: DocumentController) -> None:
    while True:
        print()
        print(f"  {_bold('--- Search by Document ID ---')}")
        print()

        doc_id: str | None = _prompt_document_id()
        if doc_id is None:
            return

        print()
        print(f"  {_info('Searching ...')}")
        result = doc_controller.get_document_detail(doc_id)

        print()
        if result.get("success"):
            print(f"  {_ok('Found 1 document:')}")
            print()
            _print_document_detail(result["document"])
        else:
            print(f"  {_info('No document found with ID')} '{doc_id}'.")

        nav: str = _navigation_prompt()
        if nav == "1":
            continue
        if nav == "2":
            return
        break


def _search_by_filename(doc_controller: DocumentController) -> None:
    while True:
        print()
        print(f"  {_bold('--- Search by File Name ---')}")
        print()

        query: str = input("  File name or keyword: ").strip()
        if not query:
            print(f"  {_err('Search cancelled')} — keyword is required.")
            return

        print()
        print(f"  {_info('Searching ...')}")
        result = doc_controller.search_my_documents(query=query)

        print()
        if result.get("success"):
            documents = result.get("documents", [])
            pagination = result.get("pagination", {})
            total = pagination.get("total", 0)

            if documents:
                _plural = 's' if total != 1 else ''
                print(
                    f"  {_ok(f'Found {total} document{_plural}')}:"
                )
                print()
                _print_document_table(documents)
            else:
                print(f"  {_info('No documents match')} '{query}'.")
        else:
            print(f"  {_err(result['error'])}")

        nav: str = _navigation_prompt()
        if nav == "1":
            continue
        if nav == "2":
            return
        break


def _show_all_documents(doc_controller: DocumentController) -> None:
    while True:
        print()
        print(f"  {_bold('--- All My Documents ---')}")
        print()

        page: int = 1
        while True:
            result = doc_controller.list_my_documents(page=page)

            if not result.get("success"):
                print(f"  {_err(result['error'])}")
                break

            documents = result.get("documents", [])
            pagination = result.get("pagination", {})

            if not documents:
                if page == 1:
                    print(f"  {_info('No documents found.')}")
                else:
                    print(f"  {_info('No more documents.')}")
                break

            total = pagination.get("total", 0)
            _page = pagination.get("page", 1)
            _total_pages = pagination.get("total_pages", 1)
            print(
                f"  {_bold(f'Page {_page}/{_total_pages}')}"
                f"  ({total} document{'s' if total != 1 else ''})"
            )
            print()
            _print_document_table(documents)
            print()

            if pagination.get("has_next"):
                choice: str = input(
                    f"  {_info('[N]ext page, [Q]uit this view: ')}"
                ).strip().lower()
                if choice == "n":
                    page += 1
                    continue
            break

        nav: str = _navigation_prompt()
        if nav == "1":
            continue
        if nav == "2":
            return
        break


# ======================================================================
# Document Download
# ======================================================================


def _handle_download(doc_controller: DocumentController) -> None:
    while True:
        print()
        print(f"  {_bold('--- Download Document ---')}")
        print()

        doc_id: str | None = _prompt_document_id()
        if doc_id is None:
            return

        output_dir: str = input("  Output directory: ").strip()
        if not output_dir:
            print(f"  {_err('Download cancelled')} — output directory is required.")
            return

        print()
        print(f"  {_info('Downloading, decrypting, and verifying integrity ...')}")
        result = doc_controller.download(
            document_id=doc_id, output_dir=output_dir
        )

        print()
        if result.get("success"):
            print(f"  {_ok(result['message'])}")
            print(f"    {_bold('Document ID')}  : {result['document_id']}")
            print(f"    {_bold('File name')}    : {result['original_filename']}")
            print(f"    {_bold('Size')}         : {result['file_size']:,} bytes")
            print(f"    {_bold('Output path')}  : {result['output_path']}")
            print(f"    {_bold('Integrity')}    : {_ok('Verified (SHA-256)')}")
        else:
            print(f"  {_err(result['error'])}")

        nav: str = _navigation_prompt()
        if nav == "1":
            continue
        if nav == "2":
            return
        break


# ======================================================================
# Document Share
# ======================================================================


def _handle_share(doc_controller: DocumentController) -> None:
    while True:
        print()
        print(f"  {_bold('--- Share Document ---')}")
        print()

        doc_id: str | None = _prompt_document_id()
        if doc_id is None:
            return

        recipient: str = input("  Recipient username: ").strip()
        if not recipient:
            print(f"  {_err('Share cancelled')} — recipient username is required.")
            return

        print()
        print(f"  {_info('Sharing document ...')}")
        result = doc_controller.share_document(
            document_id=doc_id, recipient_username=recipient
        )

        print()
        if result.get("success"):
            print(f"  {_ok(result['message'])}")
            print(f"    {_bold('Document ID')}  : {result['document_id']}")
            print(f"    {_bold('Recipient')}    : {result['recipient_username']}")
            print(f"    {_bold('Permission')}   : {result['permission']}")
        else:
            print(f"  {_err(result['error'])}")

        nav: str = _navigation_prompt()
        if nav == "1":
            continue
        if nav == "2":
            return
        break


# ======================================================================
# Shared Documents
# ======================================================================


def _handle_shared_documents(doc_controller: DocumentController) -> None:
    while True:
        print()
        print(f"  {_bold('--- Shared With Me ---')}")
        print()

        page: int = 1
        while True:
            result = doc_controller.list_shared_with_me(page=page)

            if not result.get("success"):
                print(f"  {_err(result['error'])}")
                break

            documents = result.get("documents", [])
            pagination = result.get("pagination", {})

            if not documents:
                if page == 1:
                    print(f"  {_info('No documents have been shared with you.')}")
                else:
                    print(f"  {_info('No more documents.')}")
                break

            total = pagination.get("total", 0)
            _page = pagination.get("page", 1)
            _total_pages = pagination.get("total_pages", 1)
            print(
                f"  {_bold(f'Page {_page}/{_total_pages}')}"
                f"  ({total} document{'s' if total != 1 else ''})"
            )
            print()
            _print_document_table(documents)
            print()

            if pagination.get("has_next"):
                choice: str = input(
                    f"  {_info('[N]ext page, [Q]uit this view: ')}"
                ).strip().lower()
                if choice == "n":
                    page += 1
                    continue
            break

        nav: str = _navigation_prompt()
        if nav == "1":
            continue
        if nav == "2":
            return
        break


# ======================================================================
# Face Enrollment (internal helper)
# ======================================================================


def _handle_face_enrollment(
    face_controller: FaceController,
    user_id: str,
    username: str,
) -> None:
    print()
    print(f"  {_bold('--- Face Enrollment ---')}")
    print()

    if not face_controller.is_available():
        print(f"  {_err('Face recognition libraries are not installed.')}")
        return

    print(f"  {_info('You will be asked to capture several facial images.')}")
    print(f"  {_info('Ensure good lighting and look directly at the camera.')}")
    print()

    input(f"  {_bold('Press Enter')} to start enrollment...")

    result: dict[str, Any] = face_controller.enroll(user_id, username)

    print()
    if result.get("success"):
        print(f"  {_ok(result['message'])}")
    else:
        print(f"  {_err(result['error'])}")


# ======================================================================
# Face Settings
# ======================================================================


def _handle_face_settings(
    face_controller: FaceController,
    controller: AuthController,
) -> None:
    if not face_controller.is_available():
        print()
        print(f"  {_bold('--- Face Recognition Settings ---')}")
        print()
        print(f"  {_err('Face recognition libraries are not installed.')}")
        return

    user = controller.get_current_user()
    if not user:
        print()
        print(f"  {_err('Could not retrieve user information.')}")
        return

    user_id: str = user["user_id"]
    username: str = user["username"]

    while True:
        print()
        print(f"  {_bold('--- Face Recognition Settings ---')}")
        print()

        enrolled: bool = face_controller.is_enrolled(user_id)

        if enrolled:
            print(f"  {_ok('Status: Face recognition is ENABLED')} for '{username}'.")
            print()
            print(f"  {_bold('[1]')} Re-enroll Face Data")
            print(f"  {_bold('[2]')} Remove Face Enrollment")
            print(f"  {_bold('[0]')} Back")
            print()

            choice: str = input("  Enter your choice: ").strip()

            if choice == "0":
                return
            if choice == "1":
                _handle_face_enrollment(face_controller, user_id, username)
            elif choice == "2":
                confirm: str = input(
                    f"  {_err('Are you sure?')} This will remove your facial data. (y/n): "
                ).strip().lower()
                if confirm == "y":
                    result = face_controller.remove_enrollment(user_id, username)
                    print()
                    if result.get("success"):
                        print(f"  {_ok(result['message'])}")
                    else:
                        print(f"  {_err(result['error'])}")
                else:
                    print(f"  {_info('Removal cancelled.')}")
            else:
                print(f"  {_err('Invalid choice.')}")
        else:
            print(f"  Status: Face recognition is {_err('DISABLED')} for '{username}'.")
            print()
            choice = input(
                f"  {_info('Enable Face Recognition Authentication? (y/n): ')}"
            ).strip().lower()
            if choice == "y":
                _handle_face_enrollment(face_controller, user_id, username)
            else:
                print(f"  {_info('Face recognition not enabled.')}")
                return


# ======================================================================
# Audit Logs
# ======================================================================


def _handle_audit_logs(audit_controller: AuditController) -> None:
    while True:
        print()
        print(f"  {_bold('--- Audit Logs ---')}")
        print()

        page: int = 1
        per_page: int = 20

        while True:
            result = audit_controller.view_audit_logs(page=page, per_page=per_page)

            if not result.get("success"):
                print(f"  {_err(result['error'])}")
                break

            logs = result.get("logs", [])

            if not logs:
                print(f"  {_info('No audit logs found.')}")
                break

            current_page: int = result.get("page", 1)
            total_pages: int = result.get("total_pages", 1)
            total: int = result.get("total", 0)
            has_next: bool = result.get("has_next", False)
            print(
                f"  {_bold(f'Page {current_page}/{total_pages}')}"
                f"  ({total} log{'s' if total != 1 else ''})"
            )
            print()
            print(
                f"  {_C.DIM}{'TIMESTAMP':<20} {'USER':<12} {'ACTION':<22} "
                f"{'SEVERITY':<10} {'STATUS':<10} RESOURCE{_C.RESET}"
            )
            print(f"  {_C.DIM}{'-' * 80}{_C.RESET}")

            for log in logs:
                ts: str = log.get("timestamp", "")
                if hasattr(ts, "strftime"):
                    ts = ts.strftime("%Y-%m-%d %H:%M")
                else:
                    ts = str(ts)[:16]
                username: str = log.get("username", "-")[:12]
                action: str = log.get("action", "")[:22]
                severity: str = log.get("severity", "")[:10]
                status: str = log.get("status", "")[:10]
                resource: str = log.get("resource_name", log.get("resource_id", ""))[:30]
                print(
                    f"  {ts:<20} {username:<12} {action:<22} "
                    f"{severity:<10} {status:<10} {resource}"
                )

            print()
            if has_next:
                choice: str = input(
                    f"  {_info('[N]ext page, [Q]uit this view: ')}"
                ).strip().lower()
                if choice == "n":
                    page += 1
                    continue
            break

        nav: str = _navigation_prompt()
        if nav == "1":
            continue
        if nav == "2":
            return
        break


# ======================================================================
# Audit Search
# ======================================================================


def _handle_audit_search(audit_controller: AuditController) -> None:
    while True:
        print()
        print(f"  {_bold('--- Search Audit Logs ---')}")
        print()
        print(f"  {_info('Apply filters below. Leave blank to skip any filter.')}")
        print()

        username: str = input("  Username    : ").strip()
        action: str = input("  Action      : ").strip().upper()
        severity: str = input(
            "  Severity (INFO, WARNING, SECURITY_ALERT, CRITICAL): "
        ).strip().upper()
        resource_type: str = input(
            "  Resource type (USER, DOCUMENT, SESSION, SHARING, SYSTEM, AUDIT_LOG): "
        ).strip().upper()
        status: str = input(
            "  Status (SUCCESS, FAILURE, DENIED, ERROR): "
        ).strip().upper()
        date_from: str = input("  Date from (YYYY-MM-DD): ").strip()
        date_to: str = input("  Date to (YYYY-MM-DD): ").strip()

        print()
        print(f"  {_info('Searching audit logs ...')}")
        result = audit_controller.view_audit_logs(
            username=username if username else None,
            action=action if action else None,
            severity=severity if severity else None,
            resource_type=resource_type if resource_type else None,
            status=status if status else None,
            date_from=date_from if date_from else None,
            date_to=date_to if date_to else None,
            page=1,
            per_page=50,
        )

        print()
        if not result.get("success"):
            print(f"  {_err(result['error'])}")
        else:
            logs = result.get("logs", [])
            if not logs:
                print(f"  {_info('No audit logs match your search.')}")
            else:
                current_page: int = result.get("page", 1)
                total_pages: int = result.get("total_pages", 1)
                total: int = result.get("total", 0)
                _plural_log = 's' if total != 1 else ''
                print(
                    f"  {_ok(f'Found {total} log{_plural_log}')}"
                    f" (page {current_page}/{total_pages})"
                )
                print()
                for log in logs:
                    print(
                        f"  {_C.DIM}[{log.get('timestamp', '')}]{_C.RESET} "
                        f"{log.get('username', '-')} | "
                        f"{log.get('action', '')} | "
                        f"{log.get('severity', '')} | "
                        f"{log.get('status', '')} | "
                        f"{log.get('message', '')}"
                    )

        nav: str = _navigation_prompt()
        if nav == "1":
            continue
        if nav == "2":
            return
        break
