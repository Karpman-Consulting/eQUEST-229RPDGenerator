from rpd_generator.models.base_definition import BaseDefinition


class DesignDay(BaseDefinition):
    """DesignDay class"""

    bdl_command = "DESIGN-DAY"

    def __init__(self, u_name):
        super().__init__(u_name)

    def __repr__(self):
        return f"DesignDay('{self.u_name}')"
