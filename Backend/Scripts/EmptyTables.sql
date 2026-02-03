CREATE TABLE t_Agents (
    agentId INT PRIMARY KEY AUTO_INCREMENT,
    agentName VARCHAR(100) NOT NULL,
    mobile VARCHAR(15) NOT NULL UNIQUE,
    aadhar VARCHAR(12) UNIQUE,
    email VARCHAR(100) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE t_Item (
    itemId INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(150) NOT NULL,
    description TEXT,
    qty INT NOT NULL CHECK (qty >= 0),
    size VARCHAR(50),
    weight VARCHAR(50),
    manufactureYr YEAR,
    materialType VARCHAR(100),
    model VARCHAR(100),
    additionalParam1 VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE t_AvailableStock (
    itemId INT PRIMARY KEY,
    qty INT NOT NULL CHECK (qty >= 0),
    rentedOutQty INT DEFAULT 0 CHECK (rentedOutQty >= 0),
    availableQty INT GENERATED ALWAYS AS (qty - rentedOutQty) STORED,

    CONSTRAINT fk_stock_item
        FOREIGN KEY (itemId) REFERENCES t_Item(itemId)
        ON DELETE CASCADE
);

CREATE TABLE RentalPrice (
    itemId INT PRIMARY KEY,
    itemName VARCHAR(150),
    rent DECIMAL(10,2) NOT NULL,
    rentFrequency ENUM('daily', 'weekly', 'monthly') NOT NULL,

    CONSTRAINT fk_rent_item
        FOREIGN KEY (itemId) REFERENCES t_Item(itemId)
        ON DELETE CASCADE
);


CREATE TABLE t_party (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    mobile VARCHAR(15) NOT NULL,
    aadhaar VARCHAR(12),
    secondaryMobile VARCHAR(15),
    email VARCHAR(100),
    address TEXT,
    siteAddress TEXT,

    agentId INT,
    agentName VARCHAR(100),

    status ENUM('active', 'inactive', 'payment_due', 'default', 'closed')
        DEFAULT 'active',

    dateCreated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_party_agent
        FOREIGN KEY (agentId) REFERENCES t_Agents(agentId)
);


CREATE TABLE auth_tokens (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    token VARCHAR(255) NOT NULL UNIQUE,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE rentoutTxn (
    txnId BIGINT PRIMARY KEY AUTO_INCREMENT,
    partyId VARCHAR(36) NOT NULL,
    contractId BIGINT NOT NULL,
    partyName VARCHAR(150),
    agentId INT,
    agentName VARCHAR(100),
    itemId INT NOT NULL,
    itemQty INT NOT NULL CHECK (itemQty > 0),
    txnDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_rent_party
        FOREIGN KEY (partyId) REFERENCES t_party(id),

    CONSTRAINT fk_rent_agent
        FOREIGN KEY (agentId) REFERENCES t_Agents(agentId),

    CONSTRAINT fk_rent_item
        FOREIGN KEY (itemId) REFERENCES t_Item(itemId)
);


CREATE TABLE returnTxn (
    txnId BIGINT PRIMARY KEY AUTO_INCREMENT,
    partyId VARCHAR(36) NOT NULL,
    contractId BIGINT NOT NULL,
    partyName VARCHAR(150),
    agentId INT,
    agentName VARCHAR(100),
    itemId INT NOT NULL,
    itemQty INT NOT NULL CHECK (itemQty > 0),
    txnDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_return_party
        FOREIGN KEY (partyId) REFERENCES t_party(id),

    CONSTRAINT fk_return_agent
        FOREIGN KEY (agentId) REFERENCES t_Agents(agentId),

    CONSTRAINT fk_return_item
        FOREIGN KEY (itemId) REFERENCES t_Item(itemId)
);
