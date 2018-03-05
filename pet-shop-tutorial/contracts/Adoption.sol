pragma solidity ^0.4.17;


contract Adoption {
   address[16] public adopter;
   
   function adopt(uint petId) public view returns(uint){
     require(petId>=0 && petId<=15);
     adopter[petId]=msg.sender;
     return petId;

  }
  
   function getAdopter() public view returns(address[16]){
	return adopter;
   }

}
