from api.app import create_app
from api.utils.utils import dump_all_routes_to_tmp

app = create_app()
dump_all_routes_to_tmp(app)
print("Routes written to /tmp/openroad_routes.txt")
