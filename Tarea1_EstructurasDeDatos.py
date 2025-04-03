class Stack:
    def __init__(self):
        # Inicializa una pila vacía
        self.items = []

    def push(self, item):
        # Agrega un elemento a la pila
        self.items.append(item)

    def pop(self):
        # Elimina y devuelve el elemento superior de la pila
        if not self.is_empty():
            return self.items.pop()
        raise IndexError("Pop de una pila vacía")

    def peek(self):
        # Devuelve el elemento superior de la pila sin eliminarlo
        if not self.is_empty():
            return self.items[-1]
        raise IndexError("Peek de una pila vacía")

    def is_empty(self):
        # Verifica si la pila está vacía
        return len(self.items) == 0

    def size(self):
        # Devuelve el tamaño de la pila
        return len(self.items)


class Queue:
    def __init__(self):
        # Inicializa una cola vacía
        self.items = []

    def enqueue(self, item):
        # Agrega un elemento al final de la cola
        self.items.append(item)

    def dequeue(self):
        # Elimina y devuelve el elemento al frente de la cola
        if not self.is_empty():
            return self.items.pop(0)
        raise IndexError("Dequeue de una cola vacía")

    def peek(self):
        # Devuelve el elemento al frente de la cola sin eliminarlo
        if not self.is_empty():
            return self.items[0]
        raise IndexError("Peek de una cola vacía")

    def is_empty(self):
        # Verifica si la cola está vacía
        return len(self.items) == 0

    def size(self):
        # Devuelve el tamaño de la cola
        return len(self.items)


class HashTable:
    def __init__(self, size=10):
        # Inicializa una tabla hash con un tamaño dado
        self.size = size
        self.table = [[] for _ in range(size)]

    def _hash(self, key):
        # Calcula el índice hash para una clave
        return hash(key) % self.size

    def insert(self, key, value):
        # Inserta un par clave-valor en la tabla hash
        index = self._hash(key)
        for pair in self.table[index]:
            if pair[0] == key:
                pair[1] = value
                return
        self.table[index].append([key, value])

    def get(self, key):
        # Obtiene el valor asociado a una clave
        index = self._hash(key)
        for pair in self.table[index]:
            if pair[0] == key:
                return pair[1]
        raise KeyError(f"Clave {key} no encontrada")

    def delete(self, key):
        # Elimina un par clave-valor de la tabla hash
        index = self._hash(key)
        for i, pair in enumerate(self.table[index]):
            if pair[0] == key:
                del self.table[index][i]
                return
        raise KeyError(f"Clave {key} no encontrada")

    def contains(self, key):
        # Verifica si una clave existe en la tabla hash
        index = self._hash(key)
        return any(pair[0] == key for pair in self.table[index])
    


# Demostración de funcionamiento
if __name__ == "__main__":
    # Manipulación de la Pila (Stack)
    print("***** Manipulando la Pila (Stack) *****")
    stack = Stack()
    stack.push(10)  # Agregamos un elemento
    stack.push(20)  # Agregamos otro elemento
    print("Elemento en la cima de la pila:", stack.peek())  # Consultamos el elemento superior
    print("Tamaño de la pila:", stack.size())  # Consultamos el tamaño
    print("Elemento eliminado de la pila:", stack.pop())  # Eliminamos el elemento superior
    print("Elemento en la cima de la pila:", stack.peek())  # Volvemos a consultar el elemento superior
    print("¿La pila está vacía?", stack.is_empty())  # Verificamos si está vacía
    print()

    # Manipulación de la cola (Queue)
    print("***** Manipulando la Cola (Queue) *****")
    queue = Queue()
    queue.enqueue("A")  # Agregamos un elemento
    queue.enqueue("B")  # Agregamos otro elemento
    print("Elemento al frente de la cola:", queue.peek())  # Consultamos el elemento al frente
    print("Tamaño de la cola:", queue.size())  # Consultamos el tamaño
    print("Elemento eliminado de la cola:", queue.dequeue())  # Eliminamos el elemento al frente
    print("Elemento al frente de la cola:", queue.peek())  # Volvemos a consultar el elemento al frente
    print("¿La cola está vacía?", queue.is_empty())  # Verificamos si está vacía
    print()

    # Manipulación de la tabla hash (HashTable)
    print("***** Manipulando la Tabla Hash (HashTable) *****")
    hash_table = HashTable(size=5)  # Creamos una tabla hash con tamaño 5
    hash_table.insert("clave1", 20)  # Insertamos un par clave-valor
    hash_table.insert("clave2", 100)  # Insertamos otro par clave-valor
    print("Valor asociado a 'clave1':", hash_table.get("clave1"))  # Obtenemos un valor
    print("¿La tabla contiene 'clave2'?", hash_table.contains("clave2"))  # Verificamos si contiene la clave 2
    hash_table.delete("clave1")  # Eliminamos un par clave-valor
    print("¿La tabla contiene 'clave1' después de eliminarla?", hash_table.contains("clave1"))  # Verificamos si contiene la clave eliminada
    try:
        print(hash_table.get("clave1"))  # Intentamos obtener un valor eliminado (debería lanzar un error)
    except KeyError as e:
        print(e)