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

Existing 'connections'/'transport routes' between warehouses.

- source_warehouse_id
- target_warehouse_id
- transportation_time: minutes
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

Transports between distant warehouses.

- id
- source_warehouse_id
- target_warehouse_id

### Transport routes:

*Atomic Transport components.  
Connects only neighbouring warehouses.*

- id
- transport_id
- source_warehouse_id
- target_warehouse_id
- start_timestamp: datetime
- arrival_timestamp: datetime | null

### Transported stock:

*Contents of the Transport "truck(s)"*

- entry_id
- transport_id
- product_id
- count

---


## Code:

### User Interface: TUI

*Using `simple-term-menu` library*

#### Data retrieval tasks:

- show warehouses
- show warehouse details {id}:
  - capacity:
    - max capacity
    - filled capacity
    - reserved capacity
    - free capacity
  - stock
  - awaiting transports
- show active transports
- show transport details {id}:
  - stat timestamp
  - destination arrival time estimation
  - past stops, predicted stops/next destination
  - progress to the next destination
  - total progress
- show finished transports
- show transport routes
- show products

#### Data manipulation tasks:

- add stock
- add warehouse
- add product
- add transport route
- initialise transport <sup>(will make a reservation automatically)</sup>
- remove stock
- remove warehouse
- remove product
- remove transport route
- edit warehouse
- edit product
- edit route
- cancel transport <sup>(will create new transport back to start from the closest stop)</sup>

#### Debug/simulation tasks:

- time scale <sup>(time passed multiplayer)</sup>
- time offset

#### Setup tasks:

- setup:
  - create config file for db connection
  - set up the db
- edit db connection config


### DTO:

All classes will be frozen dataclasses with slots.  
To manage input data validation, separate builder/generator classes can be present.


### Pipline:

**2 async loops:**
1. Event/time/clock loop for Transport progression
2. User input loop
