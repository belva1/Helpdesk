# PERMISSION
class IsNotCreatorOfTicketException(Exception):
    pass


# STATUSES
class IsNotActiveOrInRestorationTicketException(Exception):
    pass


class IsNotActiveTicketException(Exception):
    pass


class IsNotDeclinedTicketException(Exception):
    pass


class IsNotApprovedTicketException(Exception):
    pass


class IsNotInProcessTicketException(Exception):
    pass
