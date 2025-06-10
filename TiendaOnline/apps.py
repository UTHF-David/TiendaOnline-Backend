from django.apps import AppConfig
import threading


class TiendaonlineConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'TiendaOnline'

    def ready(self):
        """
        Se ejecuta cuando la aplicación está lista.
        Inicia el scheduler para las tareas programadas de manera segura.
        """
        try:
            # Importar aquí para evitar importaciones circulares
            from .scheduler import start_scheduler
            
            # Iniciar el scheduler en un hilo separado
            def start_scheduler_thread():
                import time
                # Esperar a que la aplicación esté completamente cargada
                time.sleep(5)
                start_scheduler()
            
            # Iniciar el hilo
            scheduler_thread = threading.Thread(target=start_scheduler_thread, daemon=True)
            scheduler_thread.start()
            
        except Exception as e:
            print(f"Error al iniciar el scheduler: {e}")
