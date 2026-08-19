class MembershipNotFoundError(Exception):
    pass


class MembershipVersionConflictError(Exception):
    pass


class LastActiveOwnerError(Exception):
    pass


class InvalidInvitationError(Exception):
    pass


class InvitationAccountMismatchError(Exception):
    pass


class PendingInvitationNotFoundError(Exception):
    pass


class ActiveMemberAlreadyExistsError(Exception):
    pass


class CompanyAccessDeniedError(Exception):
    pass


class OwnerRequiredError(Exception):
    pass
