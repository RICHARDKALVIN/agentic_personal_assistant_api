package com.richardpvt.hotel_book.service;



import com.richardpvt.hotel_book.model.BookingResponse;
import com.richardpvt.hotel_book.model.Hotel;
import com.richardpvt.hotel_book.model.HotelSearchRequest;
import org.springframework.stereotype.Service;

import java.util.*;
import java.util.stream.Collectors;

@Service
public class HotelService {

    private List<Hotel> hotels = Arrays.asList(
            new Hotel(1, "Grand Palace", "Chennai", 1000, 2),
            new Hotel(2, "Sea View Inn", "Chennai", 1000, 3),
            new Hotel(3, "Budget Stay", "Chennai", 1000, 2),
            new Hotel(4, "Luxury Suites", "Chennai", 1500, 4),
            new Hotel(5, "City Lodge", "Chennai", 500, 2),
            new Hotel(6, "Royal Residency", "Bangalore", 3500, 3),
            new Hotel(7, "Metro Hotel", "Bangalore", 2200, 2)
    );

    public List<Hotel> searchHotels(HotelSearchRequest request) {

        int minBudget = request.getBudget() - 1000;
        int maxBudget = request.getBudget() + 1000;

        return hotels.stream()

                .filter(h ->
                        h.getCity().equalsIgnoreCase(request.getCity())
                                && h.getPricePerNight() >= minBudget
                                && h.getPricePerNight() <= maxBudget
                                && h.getMaxGuests() >= request.getGuests()
                )

                .limit(5)

                .collect(Collectors.toList());
    }


    public BookingResponse bookHotel(int hotelId,String name) {

        Optional<Hotel> hotel =
                hotels.stream()
                        .filter(h -> (h.getId() == hotelId || (h.getName()).equals(name)))
                        .findFirst();

        if (hotel.isPresent()) {
            return new BookingResponse(
                    "Booking successful for hotel: "
                            + hotel.get().getName(),
                    hotelId
            );
        }

        return new BookingResponse(
                "Hotel not found",
                hotelId
        );
    }
}