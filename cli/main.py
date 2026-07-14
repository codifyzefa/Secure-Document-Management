from __future__ import annotations

from typing import Any

from controllers.auth_controller import AuthController
from controllers.audit_controller import AuditController
from controllers.document_controller import DocumentController
from controllers.face_controller import FaceController
from logger.logging_config import get_logger

logger = get_logger(__name__)

WELCOME_ART = r"""
   ======================================================
        Secure Document Management System  v1.0.0
                 Information Security
   ======================================================
"""

DOC_TABLE_HEADER: str = (
    f"  {'DOCUMENT ID':<14} {'FILENAME':<36} {'SIZE':>10}  {'STATUS':<8}"
)
DOC_TABLE_SEPARATOR: str = "  " + "-" * 72


def display_welcome() -> None:
    print(WELCOME_ART)


def _is_admin(controller: AuthController) -> bool:
    user = controller.get_current_user()
    return user is not None and user.get("role") == "admin"


def _navigation_prompt() -> str:
    print()
    print("  [1] Perform Again")
    print("  [2] Back")
    print("  [0] Return to Main Menu")
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
    print(f"  Document ID      : {doc['document_id']}")
    print(f"  Filename         : {doc['original_filename']}")
    print(f"  Type             : {doc['mime_type']}")
    print(f"  Size             : {doc['file_size_display']} ({doc['file_size']:,} bytes)")
    print(f"  SHA-256          : {doc['sha256_hash']}")
    print(f"  Status           : {doc['status']}")
    print(f"  Shared with      : {doc['shared_with_count']} user(s)")
    print(f"  Created          : {doc['created_at']}")
    print(f"  Updated          : {doc['updated_at']}")


def _prompt_document_id() -> str | None:
    doc_id: str = input("  Document ID (e.g. DOC-0001): ").strip().upper()
    if not doc_id:
        print("  Operation cancelled — Document ID is required.")
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
            print("  Goodbye.")
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
            print("  Invalid choice. Please try again.")


def _print_menu(controller: AuthController) -> None:
    print("  \u250c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2510")
    if controller.is_authenticated():
        user = controller.get_current_user()
        is_admin: bool = user is not None and user.get("role") == "admin"
        print(
            f"  \u2502  Logged in as {user['username']:<20}\u2502"
            if user
            else "  \u2502  Logged in                              \u2502"
        )
        print("  \u251c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2524")
        print("  \u2502  [3] Logout                           \u2502")
        print("  \u2502  [4] Upload Document                  \u2502")
        print("  \u2502  [5] My Documents                     \u2502")
        print("  \u2502  [6] Document Details                 \u2502")
        print("  \u2502  [7] Search Documents                 \u2502")
        print("  \u2502  [8] Download Document                \u2502")
        print("  \u2502  [9] Share Document                    \u2502")
        print("  \u2502  [10] Shared With Me                   \u2502")
        if is_admin:
            print("  \u251c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2524")
            print("  \u2502  [11] View Audit Logs                 \u2502")
            print("  \u2502  [12] Search Audit Logs               \u2502")
        print("  \u251c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2524")
        print("  \u2502  [13] Face Settings                    \u2502")
    else:
        print("  \u2502  Main Menu                            \u2502")
        print("  \u251c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2524")
        print("  \u2502  [1] Register                         \u2502")
        print("  \u2502  [2] Login (Password)                  \u2502")
        print("  \u2502  [3] Login (Face Recognition)          \u2502")
    print("  \u2502  [0] Exit                              \u2502")
    print("  \u2514\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2518")


# ======================================================================
# Registration & Login
# ======================================================================


def _handle_registration(
    controller: AuthController,
    face_controller: FaceController,
) -> None:
    print()
    print("  --- User Registration ---")
    print()

    if controller.is_authenticated():
        print("  You are already logged in.")
        return

    username: str = input("  Username        : ").strip()
    if not username:
        print("  Registration cancelled — username is required.")
        return

    password: str = input("  Password        : ")

    print()
    print("  Available roles: admin, editor, viewer")
    role: str = input("  Role            : ").strip().lower()
    if not role:
        print("  Registration cancelled — role is required.")
        return

    print()
    print("  Processing registration ...")
    result: dict[str, Any] = controller.register(
        username=username, password=password, role=role
    )

    print()
    if result.get("success"):
        print(f"  \u2713 {result['message']}")
        print(f"    Username  : {result['username']}")
        print(f"    Role      : {result['role']}")

        print()
        print("  --- Optional Face Recognition ---")
        if not face_controller.is_available():
            print(
                "  Face recognition libraries not available. "
                "Skipping enrollment."
            )
            print(
                "  Install opencv-python and face_recognition "
                "to enable this feature."
            )
        else:
            choice: str = input(
                "  Enable Face Recognition Authentication? (y/n): "
            ).strip().lower()
            if choice == "y":
                _handle_face_enrollment(
                    face_controller,
                    result["user_id"],
                    result["username"],
                )
            else:
                print(
                    "  Face recognition not enabled. "
                    "You can enable it later via [13] Face Settings."
                )
    else:
        print(f"  \u2717 {result['error']}")


def _handle_login(controller: AuthController) -> None:
    print()
    print("  --- User Login ---")
    print()

    username: str = input("  Username  : ").strip()
    if not username:
        print("  Login cancelled — username is required.")
        return

    password: str = input("  Password  : ")

    print()
    print("  Authenticating ...")
    result: dict[str, Any] = controller.login(
        username=username, password=password
    )

    print()
    if result.get("success"):
        print(f"  \u2713 {result['message']}")
    else:
        print(f"  \u2717 {result['error']}")


def _handle_face_login(face_controller: FaceController) -> None:
    print()
    print("  --- Face Recognition Login ---")
    print()

    if not face_controller.is_available():
        print(
            "  Face recognition libraries are not installed."
        )
        print(
            "  Use [2] Login (Password) instead."
        )
        return

    print("  Looking at camera...")
    result: dict[str, Any] = face_controller.login_face()

    print()
    if result.get("success"):
        print(f"  \u2713 {result['message']}")
    else:
        print(f"  \u2717 {result['error']}")


def _handle_logout(controller: AuthController) -> None:
    result: dict[str, Any] = controller.logout()
    print()
    if result.get("success"):
        print(f"  \u2713 {result['message']}")
    else:
        print(f"  \u2717 {result['error']}")


# ======================================================================
# Document Upload
# ======================================================================


def _handle_upload(doc_controller: DocumentController) -> None:
    print()
    print("  --- Upload Document ---")
    print()

    file_path: str = input("  File path  : ").strip()
    if not file_path:
        print("  Upload cancelled — file path is required.")
        return

    print()
    print("  Uploading and encrypting ...")
    result: dict[str, Any] = doc_controller.upload(file_path)

    print()
    if result.get("success"):
        print(f"  \u2713 {result['message']}")
        print(f"    Document ID  : {result['document_id']}")
        print(f"    File name    : {result['original_filename']}")
        print(f"    Size         : {result['file_size']:,} bytes")
        print(f"    MIME type    : {result['mime_type']}")
        print(f"    SHA-256      : {result['sha256_hash']}")
    else:
        print(f"  \u2717 {result['error']}")


# ======================================================================
# Document Listing (My Documents)
# ======================================================================


def _handle_list_documents(doc_controller: DocumentController) -> None:
    while True:
        print()
        print("  --- My Documents ---")
        print()

        page: int = 1
        while True:
            result = doc_controller.list_my_documents(page=page)

            if not result.get("success"):
                print(f"  \u2717 {result['error']}")
                break

            documents = result.get("documents", [])
            pagination = result.get("pagination", {})

            if not documents:
                if page == 1:
                    print("  No documents found.")
                else:
                    print("  No more documents.")
                break

            total = pagination.get("total", 0)
            print(
                f"  Page {pagination['page']}/{pagination['total_pages']}"
                f"  ({total} document{'s' if total != 1 else ''})"
            )
            print()
            _print_document_table(documents)
            print()

            if pagination.get("has_next"):
                choice: str = input(
                    "  [N]ext page, [Q]uit this view: "
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
# Document Detail
# ======================================================================


def _handle_document_detail(doc_controller: DocumentController) -> None:
    while True:
        print()
        print("  --- Document Details ---")
        print()
        print("  Enter a Document ID to view its full details.")
        print()

        doc_id: str | None = _prompt_document_id()
        if doc_id is None:
            return

        print()
        print("  Fetching details ...")
        result = doc_controller.get_document_detail(doc_id)

        print()
        if result.get("success"):
            _print_document_detail(result["document"])
        else:
            print(f"  \u2717 {result['error']}")

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
        print("  --- Search Documents ---")
        print()
        print("  [1] Search by Document ID")
        print("  [2] Search by File Name")
        print("  [3] Show All Documents")
        print("  [0] Back")
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
            print("  Invalid choice.")
            continue


def _search_by_document_id(doc_controller: DocumentController) -> None:
    while True:
        print()
        print("  --- Search by Document ID ---")
        print()

        doc_id: str | None = _prompt_document_id()
        if doc_id is None:
            return

        print()
        print("  Searching ...")
        result = doc_controller.get_document_detail(doc_id)

        print()
        if result.get("success"):
            print(f"  Found 1 document:")
            print()
            _print_document_detail(result["document"])
        else:
            print(f"  No document found with ID '{doc_id}'.")

        nav: str = _navigation_prompt()
        if nav == "1":
            continue
        if nav == "2":
            return
        break


def _search_by_filename(doc_controller: DocumentController) -> None:
    while True:
        print()
        print("  --- Search by File Name ---")
        print()

        query: str = input("  File name or keyword: ").strip()
        if not query:
            print("  Search cancelled — keyword is required.")
            return

        print()
        print("  Searching ...")
        result = doc_controller.search_my_documents(query=query)

        print()
        if result.get("success"):
            documents = result.get("documents", [])
            pagination = result.get("pagination", {})
            total = pagination.get("total", 0)

            if documents:
                print(
                    f"  Found {total} document{'s' if total != 1 else ''}:"
                )
                print()
                _print_document_table(documents)
            else:
                print(f"  No documents match '{query}'.")
        else:
            print(f"  \u2717 {result['error']}")

        nav: str = _navigation_prompt()
        if nav == "1":
            continue
        if nav == "2":
            return
        break


def _show_all_documents(doc_controller: DocumentController) -> None:
    while True:
        print()
        print("  --- All My Documents ---")
        print()

        page: int = 1
        while True:
            result = doc_controller.list_my_documents(page=page)

            if not result.get("success"):
                print(f"  \u2717 {result['error']}")
                break

            documents = result.get("documents", [])
            pagination = result.get("pagination", {})

            if not documents:
                if page == 1:
                    print("  No documents found.")
                else:
                    print("  No more documents.")
                break

            total = pagination.get("total", 0)
            print(
                f"  Page {pagination['page']}/{pagination['total_pages']}"
                f"  ({total} document{'s' if total != 1 else ''})"
            )
            print()
            _print_document_table(documents)
            print()

            if pagination.get("has_next"):
                choice: str = input(
                    "  [N]ext page, [Q]uit this view: "
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
        print("  --- Download Document ---")
        print()

        doc_id: str | None = _prompt_document_id()
        if doc_id is None:
            return

        output_dir: str = input("  Output directory: ").strip()
        if not output_dir:
            print("  Download cancelled — output directory is required.")
            return

        print()
        print("  Downloading, decrypting, and verifying integrity ...")
        result = doc_controller.download(
            document_id=doc_id, output_dir=output_dir
        )

        print()
        if result.get("success"):
            print(f"  \u2713 {result['message']}")
            print(f"    Document ID  : {result['document_id']}")
            print(f"    File name    : {result['original_filename']}")
            print(f"    Size         : {result['file_size']:,} bytes")
            print(f"    Output path  : {result['output_path']}")
            print("    Integrity    : Verified (SHA-256)")
        else:
            print(f"  \u2717 {result['error']}")

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
        print("  --- Share Document ---")
        print()

        doc_id: str | None = _prompt_document_id()
        if doc_id is None:
            return

        recipient: str = input("  Recipient username: ").strip()
        if not recipient:
            print("  Share cancelled — recipient username is required.")
            return

        print()
        print("  Sharing document ...")
        result = doc_controller.share_document(
            document_id=doc_id, recipient_username=recipient
        )

        print()
        if result.get("success"):
            print(f"  \u2713 {result['message']}")
            print(f"    Document ID  : {result['document_id']}")
            print(f"    Recipient    : {result['recipient_username']}")
            print(f"    Permission   : {result['permission']}")
        else:
            print(f"  \u2717 {result['error']}")

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
        print("  --- Shared With Me ---")
        print()

        page: int = 1
        while True:
            result = doc_controller.list_shared_with_me(page=page)

            if not result.get("success"):
                print(f"  \u2717 {result['error']}")
                break

            documents = result.get("documents", [])
            pagination = result.get("pagination", {})

            if not documents:
                if page == 1:
                    print("  No documents have been shared with you.")
                else:
                    print("  No more documents.")
                break

            total = pagination.get("total", 0)
            print(
                f"  Page {pagination['page']}/{pagination['total_pages']}"
                f"  ({total} document{'s' if total != 1 else ''})"
            )
            print()
            _print_document_table(documents)
            print()

            if pagination.get("has_next"):
                choice: str = input(
                    "  [N]ext page, [Q]uit this view: "
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
    print("  --- Face Enrollment ---")
    print()

    if not face_controller.is_available():
        print(
            "  Face recognition libraries are not installed."
        )
        return

    print("  You will be asked to capture several facial images.")
    print("  Ensure good lighting and look directly at the camera.")
    print()

    input("  Press Enter to start enrollment...")

    result: dict[str, Any] = face_controller.enroll(user_id, username)

    print()
    if result.get("success"):
        print(f"  \u2713 {result['message']}")
    else:
        print(f"  \u2717 {result['error']}")


# ======================================================================
# Face Settings
# ======================================================================


def _handle_face_settings(
    face_controller: FaceController,
    controller: AuthController,
) -> None:
    if not face_controller.is_available():
        print()
        print("  --- Face Recognition Settings ---")
        print()
        print(
            "  Face recognition libraries are not installed."
        )
        return

    user = controller.get_current_user()
    if not user:
        print()
        print("  Could not retrieve user information.")
        return

    user_id: str = user["user_id"]
    username: str = user["username"]

    while True:
        print()
        print("  --- Face Recognition Settings ---")
        print()

        enrolled: bool = face_controller.is_enrolled(user_id)

        if enrolled:
            print(f"  Status: Face recognition is ENABLED for '{username}'.")
            print()
            print("  [1] Re-enroll Face Data")
            print("  [2] Remove Face Enrollment")
            print("  [0] Back")
            print()

            choice: str = input("  Enter your choice: ").strip()

            if choice == "0":
                return
            if choice == "1":
                _handle_face_enrollment(face_controller, user_id, username)
            elif choice == "2":
                confirm: str = input(
                    "  Are you sure? This will remove your facial data. (y/n): "
                ).strip().lower()
                if confirm == "y":
                    result = face_controller.remove_enrollment(user_id, username)
                    print()
                    if result.get("success"):
                        print(f"  \u2713 {result['message']}")
                    else:
                        print(f"  \u2717 {result['error']}")
                else:
                    print("  Removal cancelled.")
            else:
                print("  Invalid choice.")
        else:
            print(f"  Status: Face recognition is DISABLED for '{username}'.")
            print()
            choice = input(
                "  Enable Face Recognition Authentication? (y/n): "
            ).strip().lower()
            if choice == "y":
                _handle_face_enrollment(face_controller, user_id, username)
            else:
                print("  Face recognition not enabled.")
                return


# ======================================================================
# Audit Logs
# ======================================================================


def _handle_audit_logs(audit_controller: AuditController) -> None:
    while True:
        print()
        print("  --- Audit Logs ---")
        print()

        page: int = 1
        per_page: int = 20

        while True:
            result = audit_controller.view_audit_logs(page=page, per_page=per_page)

            if not result.get("success"):
                print(f"  \u2717 {result['error']}")
                break

            logs = result.get("logs", [])

            if not logs:
                print("  No audit logs found.")
                break

            current_page: int = result.get("page", 1)
            total_pages: int = result.get("total_pages", 1)
            total: int = result.get("total", 0)
            has_next: bool = result.get("has_next", False)
            print(
                f"  Page {current_page}/{total_pages}"
                f"  ({total} log{'s' if total != 1 else ''})"
            )
            print()
            print(
                f"  {'TIMESTAMP':<20} {'USER':<12} {'ACTION':<22} "
                f"{'SEVERITY':<10} {'STATUS':<10} RESOURCE"
            )
            print(f"  {'-' * 80}")

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
                    "  [N]ext page, [Q]uit this view: "
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
        print("  --- Search Audit Logs ---")
        print()
        print("  Apply filters below. Leave blank to skip any filter.")
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
        print("  Searching audit logs ...")
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
            print(f"  \u2717 {result['error']}")
        else:
            logs = result.get("logs", [])
            if not logs:
                print("  No audit logs match your search.")
            else:
                current_page: int = result.get("page", 1)
                total_pages: int = result.get("total_pages", 1)
                total: int = result.get("total", 0)
                print(
                    f"  Found {total} log{'s' if total != 1 else ''}"
                    f" (page {current_page}/{total_pages})"
                )
                print()
                for log in logs:
                    print(
                        f"  [{log.get('timestamp', '')}] "
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
