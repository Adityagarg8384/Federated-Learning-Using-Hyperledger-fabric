package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"strconv"

	"github.com/hyperledger/fabric-chaincode-go/shim"
	"github.com/hyperledger/fabric-protos-go/peer"
)

type SmartContract struct{}

type DataInfo struct {
	ClientID    string `json:"clientID"`
	TrainCount  int    `json:"trainCount"`
	ValCount    int    `json:"valCount"`
	APIResponse string `json:"apiResponse,omitempty"`
}

func (s *SmartContract) Init(APIstub shim.ChaincodeStubInterface) peer.Response {
	fmt.Println("Init function called")
	return shim.Success(nil)
}

func (s *SmartContract) Invoke(APIstub shim.ChaincodeStubInterface) peer.Response {
	fmt.Println("Invoke function called")
	function, args := APIstub.GetFunctionAndParameters()

	switch function {
	case "StoreDatasetInfo":
		fmt.Println("StoreDatasetInfo function called")
		return s.StoreDatasetInfo(APIstub, args)
	case "RetrieveDatasetInfo":
		fmt.Println("RetrieveDatasetInfo function called")
		return s.RetrieveDatasetInfo(APIstub, args)
	case "GetAllData":
		fmt.Println("GetAllData function called")
		return s.GetAllData(APIstub)
	default:
		fmt.Println("Invalid function name")
		return shim.Error("Invalid function name")
	}
}

func (s *SmartContract) StoreDatasetInfo(APIstub shim.ChaincodeStubInterface, args []string) peer.Response {
	fmt.Println("StoreDatasetInfo function called")
	if len(args) != 3 {
		return shim.Error("Incorrect number of arguments. Expecting 3")
	}

	clientID := args[0]
	trainCount, err := strconv.Atoi(args[1])
	if err != nil {
		return shim.Error("Train count must be a numeric value")
	}

	valCount, err := strconv.Atoi(args[2])
	if err != nil {
		return shim.Error("Validation count must be a numeric value")
	}

	dataInfo := DataInfo{
		ClientID:   clientID,
		TrainCount: trainCount,
		ValCount:   valCount,
	}

	dataInfoBytes, err := json.Marshal(dataInfo)
	if err != nil {
		return shim.Error(fmt.Sprintf("Failed to marshal dataset info: %s", err))
	}

	err = APIstub.PutState(clientID, dataInfoBytes)
	if err != nil {
		return shim.Error(fmt.Sprintf("Failed to store dataset info: %s", err))
	}

	fmt.Println("StoreDatasetInfo operation successful")
	return shim.Success([]byte("Operation Successful"))
}

func (s *SmartContract) RetrieveDatasetInfo(APIstub shim.ChaincodeStubInterface, args []string) peer.Response {
	fmt.Println("RetrieveDatasetInfo function called")
	if len(args) != 1 {
		return shim.Error("Incorrect number of arguments. Expecting 1")
	}

	clientID := args[0]
	dataInfoBytes, err := APIstub.GetState(clientID)
	if err != nil {
		return shim.Error(fmt.Sprintf("Failed to read from world state: %s", err))
	}
	if dataInfoBytes == nil {
		return shim.Error(fmt.Sprintf("Dataset info for clientID %s does not exist", clientID))
	}

	fmt.Println("RetrieveDatasetInfo operation successful")
	return shim.Success(dataInfoBytes)
}

func (s *SmartContract) GetAllData(APIstub shim.ChaincodeStubInterface) peer.Response {
	fmt.Println("GetAllData function called")
	startKey := ""
	endKey := ""
	resultsIterator, err := APIstub.GetStateByRange(startKey, endKey)
	if err != nil {
		return shim.Error(fmt.Sprintf("Failed to get state by range: %s", err))
	}
	defer resultsIterator.Close()
	var results []DataInfo
	var clientIDs []string
	for resultsIterator.HasNext() {
		queryResponse, err := resultsIterator.Next()
		if err != nil {
			return shim.Error(fmt.Sprintf("Error iterating over query results: %s", err))
		}
		var dataInfo DataInfo
		err = json.Unmarshal(queryResponse.Value, &dataInfo)
		if err != nil {
			return shim.Error(fmt.Sprintf("Failed to unmarshal data: %s", err))
		}
		results = append(results, dataInfo)
		clientIDs = append(clientIDs, dataInfo.ClientID)
	}
	clientIDsBytes, err := json.Marshal(clientIDs) // Marshal clientIDs slice into JSON bytes
	if err != nil {
		return shim.Error(fmt.Sprintf("Failed to marshal client IDs: %s", err))
	}
	

	fmt.Println("GetAllData operation successful")
	return shim.Success(clientIDsBytes)
}

// func makeAPICall(clientIDsBytes []byte) (string, error) {
// 	fmt.Println("Making API call with clientIDsBytes:", string(clientIDsBytes))
// 	apiURL := "http://127.0.0.1:5000/start_simulation" // 
// 	fmt.Println("URL is ", apiURL)

// 	resp, err := http.Post(apiURL, "application/json", bytes.NewBuffer(clientIDsBytes))
// 	if err != nil {
// 		fmt.Println("Error in making request ", err)
// 		return "", err
// 	}
// 	defer resp.Body.Close()

// 	body, err := ioutil.ReadAll(resp.Body)
// 	if err != nil {
// 		fmt.Println("Error in body ", err)
// 		return "", err
// 	}

// 	fmt.Println("API call successful")
// 	return string(body), nil
// }


func main() {
	err := shim.Start(new(SmartContract))
	if err != nil {
		fmt.Printf("Error starting chaincode: %s", err)
	}
}
