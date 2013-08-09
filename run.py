# Used to launch develppment server
# (Note: production apps should use another method, such as Passenger on Dreamhost)

from calfiller import app

app.run(debug=True)