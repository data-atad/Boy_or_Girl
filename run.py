import os
from flaskapp_boy_or_girl import create_app

app = create_app()

if __name__ == "__main__":
	#app.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
	app.run(debug=True)