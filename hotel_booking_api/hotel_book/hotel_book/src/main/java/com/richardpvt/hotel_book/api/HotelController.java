package com.richardpvt.hotel_book.api;


import com.richardpvt.hotel_book.model.BookingResponse;
import com.richardpvt.hotel_book.model.Hotel;
import com.richardpvt.hotel_book.model.HotelSearchRequest;
import com.richardpvt.hotel_book.service.HotelService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/hotels")
public class HotelController {

    @Autowired
    private HotelService hotelService;


    @PostMapping("/search")
    public List<Hotel> searchHotels(
            @RequestBody HotelSearchRequest request) {

        return hotelService.searchHotels(request);
    }


    @PostMapping("/book/{id}/{name}")
    public BookingResponse bookHotel(
            @PathVariable int id,@PathVariable String name) {

        return hotelService.bookHotel(id,name);
    }
}