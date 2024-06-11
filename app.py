from Quiz import app
app.secret_key = 'secret_vegan' 

if __name__ == "__main__":
    app.run(debug=True)