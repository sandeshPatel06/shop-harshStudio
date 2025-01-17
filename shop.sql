-- Table structure for table `products`
CREATE TABLE `products` (
  `id` int NOT NULL,
  `name` varchar(255) NOT NULL,
  `price` decimal(10,2) NOT NULL,
  `description` text,
  `image_path` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
);

-- Set AUTO_INCREMENT for the `id` field in the `products` table
ALTER TABLE `products`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;
