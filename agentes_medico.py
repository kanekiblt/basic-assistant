print("AgenteSaludPersonal")
name = input("El nombre del paciente es: ")
lastname = input("El apellido del paciente es: ")

recomendaciones = []

opcion = int(input("\nSeleccione el parámetro a ingresar:\n1. Presión Arterial\n2. Nivel de Glucosa\n3. Temperatura (Fiebre)\n"))

if opcion == 1:
    presion_arterial = float(input("\nIngrese la presión arterial del paciente: "))
    
    if presion_arterial <= 140:
        print("\nLa presión arterial del paciente", name, lastname, "está en niveles normales.\n")
    elif presion_arterial > 140:
        print("\nLa presión arterial del paciente", name, lastname, "está elevada.\n")
        recomendaciones.append("- Consulte a un médico para evaluar la presión arterial.")

elif opcion == 2:
    glucosa = float(input("\nIngrese el nivel de glucosa del paciente: "))

    if glucosa <= 120:
        print("\nEl nivel de glucosa del paciente", name, lastname, "está en niveles normales.\n")
    elif glucosa > 120:
        print("\nEl nivel de glucosa del paciente", name, lastname, "está elevado.\n")
        recomendaciones.append("- Considere una dieta equilibrada y consulte a un médico para evaluar el nivel de glucosa.")

elif opcion == 3:
    fiebre = float(input("\nIngrese la temperatura del paciente: "))

    if fiebre <= 37:
        print("\nLa temperatura del paciente", name, lastname, "está en niveles normales.\n")
    elif fiebre > 37.5:
        print("\nLa temperatura del paciente", name, lastname, "está elevada.\n")
        recomendaciones.append("- Descanse y tome líquidos. Si la fiebre persiste, consulte a un médico.")

else:
    print("\nOpción no válida. Por favor, seleccione una opción válida (1, 2 o 3).")

# Imprimir recomendaciones generales
if recomendaciones:
    print("\nRecomendaciones:")
    for rec in recomendaciones:
        print(rec)
