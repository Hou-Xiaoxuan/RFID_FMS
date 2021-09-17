import com.impinj.octane.ImpinjReader;
import com.impinj.octane.OctaneSdkException;
import com.impinj.octane.Settings;
import com.impinj.octane.AntennaConfigGroup;

import java.io.BufferedOutputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.net.Socket;
import java.util.ArrayList;
import java.util.Scanner;

public class GetInfomationOfRssiAndPhase {
    static Socket socket;
    static OutputStream os;
    static BufferedOutputStream buffer;
    static Settings settings;
    static String hostname;
    static ImpinjReader reader;

    public static void main(String[] args) throws IOException, OctaneSdkException {
        try {
            // hostname = System.getProperty(SampleProperties.hostname);
            // if (hostname == null) {
            // throw new Exception("Must specify the '" + SampleProperties.hostname + "'
            // property");
            // }
            String IP = "192.168.3.110";
            reader = new ImpinjReader();

            // Connect reader
            System.out.println("Connecting to " + hostname);
            reader.connect(IP);

            // LiuYin
            // TCP'connetion build
            socket = new Socket("127.0.0.1", 1234);
            os = socket.getOutputStream();

            // LiuYin
            // write message to *.txt(change path every experiment)
            FileOutputStream outstr = new FileOutputStream(new File("./data.txt"));
            buffer = new BufferedOutputStream(outstr);

            // Get the default settings
            settings = reader.queryDefaultSettings();
            // see in item-test MaxThroughput Mode
            // 1000 最大可靠性
            // 0 最大吞吐量
            settings.setRfMode(0);
            // write by LiuYin
            settings.getReport().setIncludePhaseAngle(true);
            settings.getReport().setIncludePeakRssi(true);
            settings.getReport().setIncludeLastSeenTime(true);
            settings.getReport().setIncludeAntennaPortNumber(true);

            //
            settings.getAntennas().disableAll();
            ArrayList<Integer> antennas = new ArrayList<Integer>();
            antennas.add(1);
            // antennas.add(9);
            AntennaConfigGroup antennasConfig = settings.getAntennas();
            antennasConfig.enableById(antennas);
            settings.setAntennas(antennasConfig);
            // settings.getAntennas().enableById(antennas);

            // Apply the new settings
            reader.applySettings(settings);

            System.out.println(settings.getAntennas());
            // connect a listener
            reader.setTagReportListener(new TagReportListenerImplementation());

            // Start the reader
            reader.start();

            // 关闭连接
            System.out.println("Press Enter to exit.");
            Scanner s = new Scanner(System.in);
            s.nextLine();
            s.close();

        } catch (OctaneSdkException ex) {
            System.out.println(ex.getMessage());
        } catch (Exception ex) {
            System.out.println(ex.getMessage());
            ex.printStackTrace(System.out);
        } finally {
            // TCP'connection shutdown
            if (os != null)
                os.close();
            if (socket != null)
                socket.close();

            // Close file write
            if (buffer != null) {
                buffer.flush();
                buffer.close();
            }
            if (reader != null) {
                System.out.println("Stopping  " + hostname);
                reader.stop();
            }
            if (reader != null) {
                System.out.println("Disconnecting from " + hostname);
                reader.disconnect();
            }

            System.out.println("Done");
        }
    }

    public static void start_reader() throws IOException, OctaneSdkException {
        try {
            hostname = System.getProperty(SampleProperties.hostname);
            if (hostname == null) {
                throw new Exception("Must specify the '" + SampleProperties.hostname + "' property");
            }

            reader = new ImpinjReader();

            // Connect
            System.out.println("Connecting to " + hostname);
            reader.connect(hostname);

            // LiuYin
            // TCP'connetion build
            socket = new Socket("127.0.0.1", 1234);
            os = socket.getOutputStream();

            // LiuYin
            // write message to *.txt(change path every experiment)
            FileOutputStream outstr = new FileOutputStream(new File("./data.txt"));
            buffer = new BufferedOutputStream(outstr);

            // Get the default settings
            settings = reader.queryDefaultSettings();
            // see in item-test MaxThroughput Mode
            // 1000 最大可靠性
            // 0 最大吞吐量
            settings.setRfMode(0);
            // write by LiuYin
            settings.getReport().setIncludePhaseAngle(true);
            settings.getReport().setIncludePeakRssi(true);
            // settings.getReport().setIncludeChannel(true);
            settings.getReport().setIncludeLastSeenTime(true);
            settings.getReport().setIncludeAntennaPortNumber(true);
            // System.out.println(settings.getReport().getIncludePhaseAngle());
            // settings.getReport().getIncludePeakRssi();
            // settings.getReport().getIncludeChannel();

            // Apply the new settings
            reader.applySettings(settings);

            // connect a listener

            reader.setTagReportListener(new TagReportListenerImplementation());

            // Start the reader
            reader.start();

            System.out.println("Press Enter to exit.");
            Scanner s = new Scanner(System.in);
            s.nextLine();

            // 编辑器提示关闭s
            s.close();

        } catch (OctaneSdkException ex) {
            System.out.println(ex.getMessage());
        } catch (Exception ex) {
            System.out.println(ex.getMessage());
            ex.printStackTrace(System.out);
        } finally {
            // TCP'connection shutdown
            if (os != null)
                os.close();
            if (socket != null)
                socket.close();

            // Close file write
            if (buffer != null) {
                buffer.flush();
                buffer.close();
            }
            if (reader != null) {
                System.out.println("Stopping  " + hostname);
                reader.stop();
            }
            if (reader != null) {
                System.out.println("Disconnecting from " + hostname);
                reader.disconnect();
            }

            System.out.println("Done");
        }
    }
}
