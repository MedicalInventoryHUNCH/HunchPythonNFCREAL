import customtkinter
import pymongo
from pymongo import MongoClient

cluster = MongoClient("mongodb+srv://bernardorhyshunch:TakingInventoryIsFun@cluster0.jpb6w.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")
root = customtkinter.CTk()
root.title('Inventory taking bleh bleh bleh')
root.geometry("600x600")

def BlowJamie():
    print("Jamie Blown")

buttonstuff = customtkinter.CTkButton(root,
                                      text="Blow Jamie",
                                      command=BlowJamie,
                                      width=298,
                                      height=100,
                                      text_color="Black",
                                      hover_color="White"
                                      )
buttonstuff.pack(pady=20)

root.mainloop()

#TS SUCKS delete it