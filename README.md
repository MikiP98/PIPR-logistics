[//]: # (
Należy zaprojektować i zaimplementować system obsługi sieci logistycznej.
Program powinien pozwalać na obsługę sieci magazynów oraz transportu towarów
między nimi. W szczególności, powinien uwzględniać:
- Istniejące połączenia między magazynami
- Czasy transportu między magazynami
- Aktualny stan różnych produktow w magazynach
- Całkowitą maksymalną pojemność magazynów.
- Rezerwację miejsca w magazynie na nadchodzące transporty
)
[//]: # (
Program powinien umożliwiać:
- Wyświetlenie stanu magazynu,
- Wyświetlenie aktualnie trwających przejazdów,
- Wyświetlenie całkowitego rozłożenia wybranego produktu po magazynach w sieci,
- Dodanie/odebranie produktów do magazynu,
- Rozpoczęcie transportu najkrótszą ścieżką między dowolnymi dwoma magazynami,
- Przewinięcie czasu "do przodu",
- Wczytanie i zapis do pliku aktualnego stanu sieci.
)


# Project logistics

## Package manager: UV

---


# Database:

## Tables:

### Warehouses:

- id
- capacity
- reserved_capacity

### Connections:

- source_warehouse_id
- target_warehouse_id
- transportation_time: 
- two_way: bool

### Products:

- id
- name
- barcode
- mass

<br>

### Stock:

- entry_id
- product_id
- warehouse_id
- count

### Transports:

- source_warehouse_id
- target_warehouse_id
- star_timestamp