using BusBooking.Api.Data;
using BusBooking.Api.DTOs;
using BusBooking.Api.Models;
using BusBooking.Api.Services;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

namespace BusBooking.Api.Controllers;

[ApiController]
[Route("api/[controller]")]
public class AuthController : ControllerBase
{
    private readonly ApplicationDbContext _db;
    private readonly IAuthService _authService;

    public AuthController(ApplicationDbContext db, IAuthService authService)
    {
        _db = db;
        _authService = authService;
    }

    [HttpPost("register")]
    public async Task<ActionResult<AuthResponse>> Register(RegisterRequest request)
    {
        if (await _db.Users.AnyAsync(u => u.Email == request.Email))
            return Conflict(new { message = "An account with this email already exists." });

        var (hash, salt) = _authService.HashPassword(request.Password);

        var user = new User
        {
            FullName = request.FullName,
            Email = request.Email,
            PasswordHash = hash,
            PasswordSalt = salt,
            Phone = request.Phone,
            CreatedAtUtc = DateTime.UtcNow
        };

        _db.Users.Add(user);
        await _db.SaveChangesAsync();

        var token = _authService.GenerateJwtToken(user.UserId, user.Email, user.FullName);
        return Ok(new AuthResponse(user.UserId, user.FullName, user.Email, token));
    }

    [HttpPost("login")]
    public async Task<ActionResult<AuthResponse>> Login(LoginRequest request)
    {
        var user = await _db.Users.FirstOrDefaultAsync(u => u.Email == request.Email);
        if (user is null || !_authService.VerifyPassword(request.Password, user.PasswordHash, user.PasswordSalt))
            return Unauthorized(new { message = "Invalid email or password." });

        var token = _authService.GenerateJwtToken(user.UserId, user.Email, user.FullName);
        return Ok(new AuthResponse(user.UserId, user.FullName, user.Email, token));
    }
}
