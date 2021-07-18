import com.impinj.octane.ImpinjReader;
import com.impinj.octane.OctaneSdkException;
import com.impinj.octane.Settings;

import java.io.BufferedOutputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.net.Socket;
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
            // os.close();
            socket.close();

            // Close file write
            buffer.flush();
            buffer.close();

            System.out.println("Stopping  " + hostname);
            reader.stop();

            System.out.println("Disconnecting from " + hostname);
            reader.disconnect();

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
            // os.close();
            socket.close();

            // Close file write
            buffer.flush();
            buffer.close();

            System.out.println("Stopping  " + hostname);
            reader.stop();

            System.out.println("Disconnecting from " + hostname);
            reader.disconnect();

            System.out.println("Done");
        }
    }
}
