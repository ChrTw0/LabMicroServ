import { Text, View, StyleSheet } from 'react-native';

// Este es el componente de inicio que Expo buscará
export default function App() {
  return (
    <View style={styles.container}>
      <Text>¡Frontend de Laboratorio Clínico Cargado!</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#fff',
  },
});