import React, { createContext, useContext, useState, useEffect, useRef } from 'react';
import { getCarrito, addToCarrito, updateCarritoItem, removeFromCarrito, verificarExpiracionCarrito, limpiarCarrito } from '../api/datos.api';
import Swal from 'sweetalert2';

// Crear el contexto del carrito
const CartContext = createContext();

export function CartProvider({ children }) {
    const [cart, setCart] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const timerRef = useRef(null);
    const INACTIVITY_TIMEOUT = 1 * 60 * 1000; // 1 minuto en milisegundos
    const checkIntervalRef = useRef(null);
    const lastRemovedIndexRef = useRef(-1); // Para llevar el control del último producto removido

    // Función para reiniciar el temporizador
    const resetTimer = () => {
        if (timerRef.current) {
            clearTimeout(timerRef.current);
        }
        timerRef.current = setTimeout(handleInactivity, INACTIVITY_TIMEOUT);
        lastRemovedIndexRef.current = -1; // Resetear el índice cuando hay actividad
    };

    // Función para manejar la inactividad
    const handleInactivity = async () => {
        if (cart.length > 0) {
            try {
                // Obtener el siguiente índice a procesar
                const nextIndex = (lastRemovedIndexRef.current + 1) % cart.length;
                const itemToRemove = cart[nextIndex];

                // Verificar expiración del producto específico
                const { productos_expirados } = await verificarExpiracionCarrito();
                
                if (productos_expirados && productos_expirados.length > 0) {
                    // Actualizar el carrito local
                    await loadCart();
                    
                    // Mostrar mensaje de producto expirado
                    Swal.fire({
                        icon: 'warning',
                        title: 'Producto expirado',
                        text: `El producto "${itemToRemove.producto_nombre}" ha expirado y ha sido removido del carrito.`,
                    });

                    // Actualizar el índice del último producto removido
                    lastRemovedIndexRef.current = nextIndex;
                }
            } catch (error) {
                console.error('Error al verificar expiración:', error);
            }
        }
    };

    // Función para verificar expiración periódicamente
    const startExpirationCheck = () => {
        if (checkIntervalRef.current) {
            clearInterval(checkIntervalRef.current);
        }
        
        checkIntervalRef.current = setInterval(async () => {
            if (cart.length > 0) {
                try {
                    // Obtener el siguiente índice a procesar
                    const nextIndex = (lastRemovedIndexRef.current + 1) % cart.length;
                    const itemToRemove = cart[nextIndex];

                    const { productos_expirados } = await verificarExpiracionCarrito();
                    if (productos_expirados && productos_expirados.length > 0) {
                        await loadCart();
                        // Actualizar el índice del último producto removido
                        lastRemovedIndexRef.current = nextIndex;
                    }
                } catch (error) {
                    console.error('Error en verificación periódica:', error);
                }
            }
        }, INACTIVITY_TIMEOUT);
    };

    // Efecto para manejar eventos de actividad del usuario
    useEffect(() => {
        const events = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart'];
        
        const handleUserActivity = () => {
            resetTimer();
        };

        events.forEach(event => {
            document.addEventListener(event, handleUserActivity);
        });

        // Iniciar el temporizador y la verificación periódica
        resetTimer();
        startExpirationCheck();

        // Limpiar eventos y temporizadores al desmontar
        return () => {
            events.forEach(event => {
                document.removeEventListener(event, handleUserActivity);
            });
            if (timerRef.current) {
                clearTimeout(timerRef.current);
            }
            if (checkIntervalRef.current) {
                clearInterval(checkIntervalRef.current);
            }
        };
    }, [cart.length]); // Dependencia en cart.length para reiniciar cuando cambie el carrito

    // Cargar el carrito al iniciar
    useEffect(() => {
        loadCart();
    }, []);

    const loadCart = async () => {
        try {
            setLoading(true);
            setError(null);
            const carritoData = await getCarrito();
            setCart(carritoData);
        } catch (error) {
            console.error('Error al cargar el carrito:', error);
            setError(error.message);
            setCart([]);
        } finally {
            setLoading(false);
        }
    };

    const addToCart = async (product, quantity) => {
        try {
            const token = localStorage.getItem('token');
            if (!token) {
                throw new Error('Debes iniciar sesión para agregar productos al carrito');
            }
            
            await addToCarrito(product.id, quantity);
            await loadCart(); // Recargar el carrito después de agregar
            lastRemovedIndexRef.current = -1; // Resetear el índice al agregar productos
        } catch (error) {
            console.error('Error al agregar al carrito:', error);
            if (error.message.includes('Sesión expirada') || error.response?.status === 401 || error.response?.status === 403) {
                localStorage.removeItem('token');
                localStorage.removeItem('usuario');
                throw new Error('Sesión expirada. Por favor, inicia sesión nuevamente.');
            }
            throw error;
        }
    };

    const updateCartQuantity = async (id, quantity) => {
        try {
            const token = localStorage.getItem('token');
            if (!token) {
                throw new Error('Debes iniciar sesión para actualizar el carrito');
            }
            
            await updateCarritoItem(id, quantity);
            await loadCart();
            lastRemovedIndexRef.current = -1; // Resetear el índice al actualizar cantidades
        } catch (error) {
            console.error('Error al actualizar cantidad:', error);
            if (error.response?.status === 401 || error.response?.status === 403) {
                localStorage.removeItem('token');
                localStorage.removeItem('usuario');
                throw new Error('Sesión expirada. Por favor, inicia sesión nuevamente.');
            }
            throw error;
        }
    };

    const removeFromCart = async (id) => {
        try {
            const token = localStorage.getItem('token');
            if (!token) {
                throw new Error('Debes iniciar sesión para eliminar productos del carrito');
            }
            
            await removeFromCarrito(id);
            await loadCart();
            lastRemovedIndexRef.current = -1; // Resetear el índice al eliminar manualmente
        } catch (error) {
            console.error('Error al eliminar del carrito:', error);
            if (error.response?.status === 401 || error.response?.status === 403) {
                localStorage.removeItem('token');
                localStorage.removeItem('usuario');
                throw new Error('Sesión expirada. Por favor, inicia sesión nuevamente.');
            }
            throw error;
        }
    };

    const clearCart = async () => {
        try {
            await limpiarCarrito();
            setCart([]);
            lastRemovedIndexRef.current = -1; // Resetear el índice al limpiar el carrito
            console.log('Carrito limpiado exitosamente');
        } catch (error) {
            console.error('Error al limpiar el carrito:', error);
            throw error;
        }
    };

    // Calcular el total del carrito
    const cartTotal = cart.reduce((total, item) => {
        return total + (Number(item.producto_precio) * item.cantidad_prod);
    }, 0);

    // Proveer el contexto a los componentes hijos
    return (
        <CartContext.Provider value={{
            cart,
            loading,
            error,
            addToCart,
            removeFromCart,
            updateCartQuantity,
            cartTotal,
            clearCart,
            refreshCart: loadCart
        }}>
            {children}
        </CartContext.Provider>
    );
}

// Hook personalizado para usar el contexto del carrito
export function useCart() {
    return useContext(CartContext);
} 