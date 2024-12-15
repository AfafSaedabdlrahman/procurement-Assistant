### About Dataset

#### Context
This dataset contains detailed records of large procurement transactions made by the State of California, capturing information on purchases of goods and services across various state departments. It is ideal for analyzing procurement trends, supplier performance, and cost optimization in state acquisitions.

#### Data Description
The dataset consists of **346,018 observations** with **31 variables**.

- **Creation Date**: The date the transaction was created.
- **Purchase Date**: The date the purchase order was entered, which can sometimes be backdated. The creation date is used if the purchase date is missing.
- **Fiscal Year**: The fiscal year derived based on the creation date, starting July 1 and ending June 30.
- **LPA Number**: The Leveraged Procurement Agreement (LPA) or contract number. If present, the amount is considered contract spend.
- **Purchase Order Number**: A unique identifier for the purchase order, though not always unique across departments.
- **Requisition Number**: A unique identifier for the requisition; requisition numbers may be duplicated across departments.
- **Acquisition Type**: The type of acquisition (e.g., Non-IT Goods, Non-IT Services, IT Goods, IT Services).
- **Sub-Acquisition Type**: A subcategory of the acquisition type, depending on the primary acquisition type.
- **Acquisition Method**: The method used to make the purchase (e.g., competitive bid, sole source).
- **Sub-Acquisition Method**: A subcategory of the acquisition method.
- **Department Name**: The purchasing department involved in the transaction.
- **Supplier Code**: A unique code identifying the supplier.
- **Supplier Name**: The supplier’s name registered with the State of California.
- **Supplier Qualifications**: Information on the supplier's certifications (e.g., small business, disabled veteran business enterprise).
- **Supplier Zip Code**: The supplier's zip code.
- **CalCard**: Indicates whether a State credit card (CalCard) was used for the purchase (Yes/No).
- **Item Name**: The name of the purchased item(s).
- **Item Description**: A description of the item(s).
- **Quantity**: The quantity of items purchased.
- **Unit Price**: The unit price of the items.
- **Total Price**: The total price of the items purchased (excluding taxes and shipping costs).
- **Classification Codes**: The UNSPSC classification codes for the purchased items, which may contain more than one UNSPSC number.
- **Normalized UNSPSC**: The normalized UNSPSC code identifying the entire purchase order.
- **Commodity Title**: A title corresponding to the commodity based on the 8-digit normalized UNSPSC code.
- **Class**: A class number based on the 8-digit normalized UNSPSC code.
- **Class Title**: A class title based on the 8-digit normalized UNSPSC code.
- **Family**: A family number based on the 8-digit normalized UNSPSC code.
- **Family Title**: A family title based on the 8-digit normalized UNSPSC code.
- **Segment**: A segment number based on the 8-digit normalized UNSPSC code.
- **Segment Title**: A segment title based on the 8-digit normalized UNSPSC code.

#### Source
This dataset is available on Kaggle: [Large Purchases by the State of California](https://www.kaggle.com/datasets/sohier/large-purchases-by-the-state-of-ca/data).
