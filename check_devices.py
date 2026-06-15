import pandas as pd

df = pd.read_csv("devices_master.csv")

print("Total Devices:")
print(df["device"].nunique())

print("\nCategories:")
print(df["category"].value_counts())

print("\nPhones:")
print(len(df[df["category"]=="Phones"]))

print("\nTablets:")
print(len(df[df["category"]=="Tablets"]))

print("\nAI PCs:")
print(len(df[df["category"]=="AI PCs"]))