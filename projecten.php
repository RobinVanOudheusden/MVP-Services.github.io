<!DOCTYPE html>
<html>
<head>
    <title>MVP-Services Projecten</title>
    <link rel="stylesheet" type="text/css" href="style.css">
</head>
<body>
    <h1>Projecten Pagina</h1>
    <div class="container">
        <?php
        $servername = "localhost";
        $username = "root";
        $password = "mysql";
        $dbname = "mydatabase";

        // Create connection
        $conn = new mysqli($servername, $username, $password, $dbname);

        // Check connection
        if ($conn->connect_error) {
            die("Connection failed: " . $conn->connect_error);
        }

        $sql = "SELECT title, description, image1, image2, image3 FROM uploads";
        $result = $conn->query($sql);

        if ($result->num_rows > 0) {
            while($row = $result->fetch_assoc()) {
                echo '<div class="card">';
                echo '<h2>' . $row["title"] . '</h2>';
                echo '<p>' . $row["description"] . '</p>';
                echo '<div class="image-container">';
                for ($i = 1; $i <= 3; $i++) {
                    $image = $row["image$i"];
                    if ($image) {
                        echo '<img src="data/' . $row["title"] . '/' . $image . '" alt="Image">';
                    }
                }
                echo '</div>'; // Close image-container
                echo '</div>'; // Close card
            }
        } else {
            echo "No data found.";
        }
        $conn->close();
        ?>
    </div> <!-- Close container -->
</body>
</html>