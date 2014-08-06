//
//  main.cpp
//  keyzio-cmd
//
//  Created by James FitzGerald on 8/5/14.
//  Copyright (c) 2014 SafeNet Labs. All rights reserved.
//

#include <iostream>
#include "../../keyzio_api.h"

int main(int argc, const char * argv[])
{

    // insert code here...
    std::cout << "Hello, World!\n";
    
    int rc = authenticate("james", "Safenet_1");
    if (rc == 0) {
        std::cout << "Successfully authenticated to keyzio\n";
    } else {
        std::cout << "Authentication failed, error: " << rc << std::endl;
    }
    return 0;
}

