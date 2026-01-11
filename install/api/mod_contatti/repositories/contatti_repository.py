from typing import List, Optional
from datetime import datetime
import pyodbc
from ..models.contatto_models import ContattoCreate, ContattoUpdate, StatoContatto


class ContattiRepository:
    """Repository per gestire le operazioni CRUD sui contatti"""

    def __init__(self, dsn: str = "microtools-demo"):
        self.dsn = dsn

    def _get_connection(self):
        """Ottiene una connessione al database"""
        return pyodbc.connect(f"DSN={self.dsn}")

    def create(self, contatto: ContattoCreate) -> int:
        """Crea un nuovo contatto"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # Insert contatto
            cursor.execute("""
                INSERT INTO contatti (
                    nome, cognome, email, telefono, cellulare, azienda, ruolo,
                    indirizzo, citta, provincia, cap, paese, stato,
                    consenso_privacy, consenso_marketing, note
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                contatto.nome, contatto.cognome, contatto.email, contatto.telefono,
                contatto.cellulare, contatto.azienda, contatto.ruolo, contatto.indirizzo,
                contatto.citta, contatto.provincia, contatto.cap, contatto.paese or 'Italia',
                contatto.stato.value, contatto.consenso_privacy, contatto.consenso_marketing,
                contatto.note
            ))

            # Get last inserted ID
            cursor.execute("SELECT last_insert_rowid()")
            contatto_id = cursor.fetchone()[0]

            # Add to lists if specified
            if contatto.liste_ids:
                for lista_id in contatto.liste_ids:
                    cursor.execute(
                        "INSERT INTO contatto_lista (contatto_id, lista_id) VALUES (?, ?)",
                        (contatto_id, lista_id)
                    )

            conn.commit()
            return contatto_id
        finally:
            cursor.close()
            conn.close()

    def get_by_id(self, contatto_id: int, include_deleted: bool = False) -> Optional[dict]:
        """Recupera un contatto per ID"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            query = "SELECT * FROM contatti WHERE id = ?"
            params = [contatto_id]

            if not include_deleted:
                query += " AND deleted_at IS NULL"

            cursor.execute(query, params)
            row = cursor.fetchone()

            if not row:
                return None

            contatto = dict(zip([column[0] for column in cursor.description], row))

            # Get liste
            cursor.execute("""
                SELECT l.* FROM liste_contatti l
                JOIN contatto_lista cl ON l.id = cl.lista_id
                WHERE cl.contatto_id = ?
            """, (contatto_id,))

            liste = []
            for row in cursor.fetchall():
                liste.append(dict(zip([column[0] for column in cursor.description], row)))

            contatto['liste'] = liste
            return contatto
        finally:
            cursor.close()
            conn.close()

    def get_all(self, page: int = 1, page_size: int = 50, include_deleted: bool = False) -> tuple[List[dict], int]:
        """Recupera tutti i contatti con paginazione"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # Count total
            count_query = "SELECT COUNT(*) FROM contatti"
            if not include_deleted:
                count_query += " WHERE deleted_at IS NULL"

            cursor.execute(count_query)
            total = cursor.fetchone()[0]

            # Get paginated results
            query = "SELECT * FROM contatti"
            if not include_deleted:
                query += " WHERE deleted_at IS NULL"
            query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"

            offset = (page - 1) * page_size
            cursor.execute(query, (page_size, offset))

            contatti = []
            for row in cursor.fetchall():
                contatto = dict(zip([column[0] for column in cursor.description], row))

                # Get liste for each contatto
                cursor2 = conn.cursor()
                cursor2.execute("""
                    SELECT l.* FROM liste_contatti l
                    JOIN contatto_lista cl ON l.id = cl.lista_id
                    WHERE cl.contatto_id = ?
                """, (contatto['id'],))

                liste = []
                for list_row in cursor2.fetchall():
                    liste.append(dict(zip([column[0] for column in cursor2.description], list_row)))

                contatto['liste'] = liste
                cursor2.close()
                contatti.append(contatto)

            return contatti, total
        finally:
            cursor.close()
            conn.close()

    def update(self, contatto_id: int, contatto: ContattoUpdate) -> bool:
        """Aggiorna un contatto esistente"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # Build dynamic update query
            updates = []
            params = []

            if contatto.nome is not None:
                updates.append("nome = ?")
                params.append(contatto.nome)
            if contatto.cognome is not None:
                updates.append("cognome = ?")
                params.append(contatto.cognome)
            if contatto.email is not None:
                updates.append("email = ?")
                params.append(contatto.email)
            if contatto.telefono is not None:
                updates.append("telefono = ?")
                params.append(contatto.telefono)
            if contatto.cellulare is not None:
                updates.append("cellulare = ?")
                params.append(contatto.cellulare)
            if contatto.azienda is not None:
                updates.append("azienda = ?")
                params.append(contatto.azienda)
            if contatto.ruolo is not None:
                updates.append("ruolo = ?")
                params.append(contatto.ruolo)
            if contatto.indirizzo is not None:
                updates.append("indirizzo = ?")
                params.append(contatto.indirizzo)
            if contatto.citta is not None:
                updates.append("citta = ?")
                params.append(contatto.citta)
            if contatto.provincia is not None:
                updates.append("provincia = ?")
                params.append(contatto.provincia)
            if contatto.cap is not None:
                updates.append("cap = ?")
                params.append(contatto.cap)
            if contatto.paese is not None:
                updates.append("paese = ?")
                params.append(contatto.paese)
            if contatto.stato is not None:
                updates.append("stato = ?")
                params.append(contatto.stato.value)
            if contatto.consenso_privacy is not None:
                updates.append("consenso_privacy = ?")
                params.append(contatto.consenso_privacy)
            if contatto.consenso_marketing is not None:
                updates.append("consenso_marketing = ?")
                params.append(contatto.consenso_marketing)
            if contatto.note is not None:
                updates.append("note = ?")
                params.append(contatto.note)

            if not updates:
                return True

            updates.append("updated_at = CURRENT_TIMESTAMP")
            params.append(contatto_id)

            query = f"UPDATE contatti SET {', '.join(updates)} WHERE id = ? AND deleted_at IS NULL"
            cursor.execute(query, params)

            # Update liste if specified
            if contatto.liste_ids is not None:
                # Remove all existing associations
                cursor.execute("DELETE FROM contatto_lista WHERE contatto_id = ?", (contatto_id,))

                # Add new associations
                for lista_id in contatto.liste_ids:
                    cursor.execute(
                        "INSERT INTO contatto_lista (contatto_id, lista_id) VALUES (?, ?)",
                        (contatto_id, lista_id)
                    )

            conn.commit()
            return cursor.rowcount > 0
        finally:
            cursor.close()
            conn.close()

    def soft_delete(self, contatto_id: int) -> bool:
        """Soft delete di un contatto (imposta deleted_at)"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "UPDATE contatti SET deleted_at = CURRENT_TIMESTAMP WHERE id = ? AND deleted_at IS NULL",
                (contatto_id,)
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            cursor.close()
            conn.close()

    def restore(self, contatto_id: int) -> bool:
        """Ripristina un contatto soft-deleted"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "UPDATE contatti SET deleted_at = NULL WHERE id = ?",
                (contatto_id,)
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            cursor.close()
            conn.close()

    def hard_delete(self, contatto_id: int) -> bool:
        """Hard delete di un contatto (eliminazione fisica)"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # Delete associations first
            cursor.execute("DELETE FROM contatto_lista WHERE contatto_id = ?", (contatto_id,))

            # Delete contatto
            cursor.execute("DELETE FROM contatti WHERE id = ?", (contatto_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            cursor.close()
            conn.close()

    def search(self, query: str, page: int = 1, page_size: int = 50) -> tuple[List[dict], int]:
        """Cerca contatti per nome, cognome, email o azienda"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            search_pattern = f"%{query}%"

            # Count total
            cursor.execute("""
                SELECT COUNT(*) FROM contatti
                WHERE deleted_at IS NULL AND (
                    nome LIKE ? OR cognome LIKE ? OR email LIKE ? OR azienda LIKE ?
                )
            """, (search_pattern, search_pattern, search_pattern, search_pattern))
            total = cursor.fetchone()[0]

            # Get results
            offset = (page - 1) * page_size
            cursor.execute("""
                SELECT * FROM contatti
                WHERE deleted_at IS NULL AND (
                    nome LIKE ? OR cognome LIKE ? OR email LIKE ? OR azienda LIKE ?
                )
                ORDER BY created_at DESC LIMIT ? OFFSET ?
            """, (search_pattern, search_pattern, search_pattern, search_pattern, page_size, offset))

            contatti = []
            for row in cursor.fetchall():
                contatto = dict(zip([column[0] for column in cursor.description], row))
                contatto['liste'] = []
                contatti.append(contatto)

            return contatti, total
        finally:
            cursor.close()
            conn.close()


class ListeContattiRepository:
    """Repository per gestire le liste di contatti"""

    def __init__(self, dsn: str = "microtools-demo"):
        self.dsn = dsn

    def _get_connection(self):
        """Ottiene una connessione al database"""
        return pyodbc.connect(f"DSN={self.dsn}")

    def create(self, nome: str, descrizione: Optional[str] = None) -> int:
        """Crea una nuova lista"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO liste_contatti (nome, descrizione) VALUES (?, ?)",
                (nome, descrizione)
            )
            cursor.execute("SELECT last_insert_rowid()")
            lista_id = cursor.fetchone()[0]
            conn.commit()
            return lista_id
        finally:
            cursor.close()
            conn.close()

    def get_all(self) -> List[dict]:
        """Recupera tutte le liste"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM liste_contatti ORDER BY nome")
            liste = []
            for row in cursor.fetchall():
                liste.append(dict(zip([column[0] for column in cursor.description], row)))
            return liste
        finally:
            cursor.close()
            conn.close()

    def get_by_id(self, lista_id: int) -> Optional[dict]:
        """Recupera una lista per ID"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM liste_contatti WHERE id = ?", (lista_id,))
            row = cursor.fetchone()

            if not row:
                return None

            return dict(zip([column[0] for column in cursor.description], row))
        finally:
            cursor.close()
            conn.close()

    def delete(self, lista_id: int) -> bool:
        """Elimina una lista"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # Delete associations first
            cursor.execute("DELETE FROM contatto_lista WHERE lista_id = ?", (lista_id,))

            # Delete lista
            cursor.execute("DELETE FROM liste_contatti WHERE id = ?", (lista_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            cursor.close()
            conn.close()
