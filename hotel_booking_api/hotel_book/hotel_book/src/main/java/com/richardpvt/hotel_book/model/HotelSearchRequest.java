package com.richardpvt.hotel_book.model;



import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDate;


@Data
@AllArgsConstructor
@NoArgsConstructor
public class HotelSearchRequest {
    private String city;
    private LocalDate checkIn;
    private LocalDate checkOut;
    private int guests;
    private int budget;
}