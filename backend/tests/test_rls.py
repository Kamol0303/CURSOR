from app.core.rls import clear_rls_context, set_rls_role, set_rls_user


def test_set_rls_role():
    set_rls_role("system")
    set_rls_user(None)
    clear_rls_context()
