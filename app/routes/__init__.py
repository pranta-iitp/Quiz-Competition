from flask import Blueprint

# Import blueprints from submodules
from .author import author_bp
from .quiz import quiz_bp
from .participant import participant_bp
#from .superuser import superuser_bp

# You can optionally create a Blueprint group if needed,
# or just expose all individual blueprints for registration
all_blueprints = [author_bp, quiz_bp, participant_bp]
