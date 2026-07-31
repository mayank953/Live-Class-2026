
# -----------------------------------------------------------------------
# VARIABLES AND DATA TYPES
# -----------------------------------------------------------------------
# A variable is a labeled box. Data type = what kind of thing is allowed
# inside that box -- you wouldn't store soup in a box labeled "books."

city = "Tokyo"                    # str   -- this is what a tool ARGUMENT looks like
temperature = 22.5                # float -- this is what a tool RESULT often looks like
is_raining = False                # bool  -- this is what a DECISION inside an agent looks like
forecast = [22.5, 23.1, 21.8]      # list  -- a sequence of readings, in order

print(type(city), type(temperature), type(is_raining), type(forecast))


# -----------------------------------------------------------------------
# F-STRINGS -- mixing variables into text
# -----------------------------------------------------------------------
# An f-string is a string with `f` right before the opening quote.
# Anything inside { } gets swapped out for the variable's real value.

print(f"The temperature in {city} is {temperature} degrees.")
print(f"That's {temperature * 9 / 5 + 32:.1f}°F.")   # math works inside { } too, :.1f rounds to 1 decimal


# -----------------------------------------------------------------------
# CONTROL FLOW -- the agent's decision-making, in miniature
# -----------------------------------------------------------------------

if is_raining:
    print("Bring an umbrella.")
else:
    print("No umbrella needed.")

for day_temp in forecast:
    if day_temp > 23:
        print(f"{day_temp}°C — warm day")
    else:
        print(f"{day_temp}°C — mild day")


if __name__ == "__main__":
    print("\nEvery one of these types and decisions reappears, unchanged, inside the agent you build later.")
