import javax.swing.*;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

public class Calculadora extends JFrame {

    public Calculadora() {
        setTitle("Calculadora de Límites y Vectores");
        setSize(400, 300);
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLocationRelativeTo(null);

        // Crear panel principal
        JPanel panel = new JPanel();
        panel.setLayout(new GridLayout(3, 1));

        // Botón para calcular límites
        JButton btnLimites = new JButton("Calcular Límites");
        btnLimites.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                calcularLimites();
            }
        });

        // Botón para operaciones con vectores
        JButton btnVectores = new JButton("Operaciones con Vectores");
        btnVectores.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                operacionesVectores();
            }
        });

        // Agregar botones al panel
        panel.add(btnLimites);
        panel.add(btnVectores);

        // Agregar panel al marco
        add(panel);
    }

    private void calcularLimites() {
        String funcion = JOptionPane.showInputDialog(this, "Introduce la función:");
        String punto = JOptionPane.showInputDialog(this, "Introduce el punto de evaluación:");

        try {
            double x = Double.parseDouble(punto);
            // Aquí puedes implementar la lógica para calcular el límite
            JOptionPane.showMessageDialog(this, "Resultado del límite: (implementación pendiente)");
        } catch (NumberFormatException ex) {
            JOptionPane.showMessageDialog(this, "Por favor, introduce un número válido para el punto.");
        }
    }

    private void operacionesVectores() {
        String vector1 = JOptionPane.showInputDialog(this, "Introduce el primer vector (separado por comas):");
        String vector2 = JOptionPane.showInputDialog(this, "Introduce el segundo vector (separado por comas):");

        try {
            double[] v1 = parseVector(vector1);
            double[] v2 = parseVector(vector2);

            if (v1.length != v2.length) {
                JOptionPane.showMessageDialog(this, "Los vectores deben tener la misma dimensión.");
                return;
            }

            // Aquí puedes implementar operaciones como suma, resta, producto escalar, etc.
            JOptionPane.showMessageDialog(this, "Resultado de la operación: (implementación pendiente)");
        } catch (NumberFormatException ex) {
            JOptionPane.showMessageDialog(this, "Por favor, introduce vectores válidos.");
        }
    }

    private double[] parseVector(String input) throws NumberFormatException {
        String[] parts = input.split(",");
        double[] vector = new double[parts.length];
        for (int i = 0; i < parts.length; i++) {
            vector[i] = Double.parseDouble(parts[i].trim());
        }
        return vector;
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> {
            Calculadora calculadora = new Calculadora();
            calculadora.setVisible(true);
        });
    }
}