import threading

from sonda import Sonda


MAX_SONDES = 8


def main():
    # Totes les sondes comparteixen el mateix senyal d'aturada.
    stop_event = threading.Event()
    cluster = []

    print("Simulador de sondes IoT")
    print(f"Es poden crear fins a {MAX_SONDES} sondes en aquesta execució.")

    try:
        while True:
            print(f"\nSondes creades: {len(cluster)}/{MAX_SONDES}")
            print("1. Crear sondes ecoLog 1000 'C'")
            print("x. Sortir i aturar totes les sondes")
            opcio = input("Selecciona una opció: ").strip().lower()

            if opcio == "x":
                break

            if opcio != "1":
                print("Opció incorrecta. Escriu 1 o x.")
                continue

            disponibles = MAX_SONDES - len(cluster)
            if disponibles == 0:
                print("Ja s'ha arribat al màxim de vuit sondes.")
                continue

            try:
                quantitat = int(input(
                    f"Quantes sondes vols crear? (1-{disponibles}): "
                ))
            except ValueError:
                print("Has d'introduir un nombre enter.")
                continue

            if not 1 <= quantitat <= disponibles:
                print(f"La quantitat ha d'estar entre 1 i {disponibles}.")
                continue

            for _ in range(quantitat):
                identificador = f"00SONDA{len(cluster) + 1:03d}"
                sonda = Sonda(identificador, stop_event)
                cluster.append(sonda)
                sonda.start()
                print(f"Sonda {identificador} creada i iniciada.")

    except (KeyboardInterrupt, EOFError):
        print("\nS'ha sol·licitat l'aturada del simulador.")

    finally:
        stop_event.set()
        print("Aturant les sondes...")
        for sonda in cluster:
            #No es pot fer join d'un fil que no ha arribat a iniciar-se.
            if sonda.ident is not None:
                sonda.join()
        print("Totes les sondes iniciades han finalitzat.")


if __name__ == "__main__":
    main()