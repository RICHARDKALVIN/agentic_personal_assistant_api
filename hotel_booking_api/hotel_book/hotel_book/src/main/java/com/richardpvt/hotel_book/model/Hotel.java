package com.richardpvt.hotel_book.model;


import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;


@Data
@AllArgsConstructor
@NoArgsConstructor
public class Hotel {

    private int id;
    private String name;
    private String city;
    private int pricePerNight;
    private int maxGuests;

}
