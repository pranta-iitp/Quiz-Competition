from app import app

if __name__ == "__main__":
    print(app.url_map)  # Shows all registered endpoints
    app.run(debug=True)
